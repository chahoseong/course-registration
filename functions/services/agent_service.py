import json
import os
from typing import List, Optional
from models.course import Course
from services.course_service import CourseService
from services.enrollment_service import EnrollmentService, EnrollmentError

class AgentService:
    def __init__(self, course_service: CourseService, enrollment_service: EnrollmentService):
        self.course_service = course_service
        self.enrollment_service = enrollment_service
        
        # Initialize OpenAI Client
        api_key = os.environ.get("OPENAI_API_KEY")
        self.init_error = None

        if not api_key:
            print("Warning: OPENAI_API_KEY is not set.")
            self.init_error = "OPENAI_API_KEY Missing"
            self.client = None
        else:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=api_key)
            except Exception as e:
                print(f"Warning: OpenAI SDK unavailable: {e}")
                self.init_error = f"OpenAI SDK Error: {str(e)}"
                self.client = None

    def chat(self, user_id: str, message: str) -> str:
        # Debug: 사용자 메시지 확인
        print(f"Agent Chat Request - User: {user_id}, Message: {message}")

        if not self.client:
            return f"죄송합니다. 서버 설정 오류로 인해 AI 에이전트를 사용할 수 없습니다. ({self.init_error})"

        # Define tools
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "list_courses",
                    "description": "수강 가능한 모든 강의 목록을 조회합니다. 강의명, 강사, 시간, 정원 정보를 포함합니다.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                    },
                },
            },
           {
                "type": "function",
                "function": {
                    "name": "get_my_enrollments",
                    "description": "사용자가 현재 신청한 수강 내역을 조회합니다.",
                    "parameters": {
                        "type": "object",
                         "properties": {},
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "enroll_course",
                    "description": "특정 강의를 수강 신청합니다. 성공 또는 실패 메시지를 반드시 반환합니다.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "course_id": {
                                "type": "string",
                                "description": "신청할 강의의 고유 ID. 사용자가 강의명을 입력했다면 먼저 list_courses로 ID를 확인해야 합니다.",
                            },
                        },
                        "required": ["course_id"],
                    },
                },
            },
        ]
        
        # System prompt
        system_instruction = f"""
        당신은 수강신청 도우미 AI 에이전트입니다. 
        학생들이 강의를 조회하고 수강신청하는 것을 도와주세요. 사용자 ID: {user_id}
        
        [매우 중요한 규칙 - 반드시 따를 것]
        1. 사용자가 "수강 신청 해줘" 등 명령을 내렸는데 **강의 ID를 정확히 말하지 않고 강의명(예: 파이썬, 리액트 등)만 언급했다면**, 
           사용자에게 되묻지 말고 **즉시 `list_courses` 도구를 호출**하세요.
        2. `list_courses` 도구의 실행 결과를 보고, 사용자가 말한 강의명과 일치하는 강의의 ID를 스스로 찾아내세요.
        3. 찾아낸 ID를 사용하여 **반드시 `enroll_course` 도구를 호출**하여 신청을 시도하세요.
        4. 사용자는 강의 ID를 모릅니다. 당신이 `list_courses`로 찾아서 처리해야 합니다.
        5. 수강 신청 완료 후 결과를 정중하게 한국어로 안내하세요.
        """

        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": message},
        ]

        try:
            # Multi-step tool loop:
            # list_courses -> enroll_course 같이 연속 tool 호출이 필요한 케이스를 끝까지 처리
            max_steps = 5
            step = 0
            enrollment_done = False

            while step < max_steps:
                # 이미 수강신청에 성공했다면, 더 이상 도구를 쓰지 말고 답변만 생성하도록 강제 ("none")
                current_tool_choice = "none" if enrollment_done else "auto"

                response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages,
                    tools=tools,
                    tool_choice=current_tool_choice,
                )
                response_message = response.choices[0].message
                tool_calls = response_message.tool_calls

                print(f"Model Response (step={step}): {response_message.content}")
                if tool_calls:
                    print(f"Tool Calls Detected (step={step}): {[tc.function.name for tc in tool_calls]}")

                if not tool_calls:
                    # Fallback 로직은 도구를 아직 안 썼을 때만 유효하거나, 
                    # enrollment_done 상태라면 그냥 답변을 리턴하면 됨.
                    if enrollment_done:
                         return response_message.content or "수강 신청이 완료되었습니다."
                         
                    # Fallback: 모델이 tool call을 누락해도 수강신청 의도는 서버에서 강제 처리
                    fallback_response = self._fallback_enroll_if_needed(user_id, message)
                    if fallback_response is not None:
                        return fallback_response
                    return response_message.content or ""

                messages.append(response_message)
                
                for tool_call in tool_calls:
                    tool_output = self._execute_tool_call(user_id, tool_call.function.name, tool_call.function.arguments)
                    messages.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": tool_call.function.name,
                            "content": tool_output,
                        }
                    )
                    
                    if tool_call.function.name == "enroll_course" and '"status": "success"' in tool_output:
                        enrollment_done = True
                
                step += 1

            return "요청을 처리하는 데 단계가 너무 많아 중단되었습니다. 다시 시도해 주세요."

        except Exception as e:
            print(f"OpenAI Error: {e}")
            return f"죄송합니다. 처리 중 문제가 발생했습니다. ({str(e)})"

    def _execute_tool_call(self, user_id: str, function_name: str, raw_args: str) -> str:
        try:
            function_args = json.loads(raw_args) if raw_args else {}
        except Exception:
            function_args = {}

        print(f"Tool Call: {function_name}, Args: {function_args}")
        tool_output = ""

        try:
            if function_name == "list_courses":
                all_courses = self.course_service.get_all_courses()
                # 필터링 로직: 이미 수강 중이거나 시간 겹치는 강의 제외
                available_courses = self._filter_available_courses(user_id, all_courses)
                tool_output = json.dumps([c.model_dump() for c in available_courses], ensure_ascii=False, default=str)

            elif function_name == "get_my_enrollments":
                enrollments = self.enrollment_service.get_student_enrollments(user_id)
                tool_output = json.dumps([e.model_dump() for e in enrollments], ensure_ascii=False, default=str)

            elif function_name == "enroll_course":
                course_id = function_args.get("course_id")
                if not course_id:
                    tool_output = json.dumps({"error": "course_id is required"}, ensure_ascii=False)
                else:
                    result = self.enrollment_service.enroll_student(user_id, course_id)
                    tool_output = json.dumps(
                        {"status": "success", "message": "수강 신청 완료", "data": result.model_dump()},
                        ensure_ascii=False,
                        default=str,
                    )
            else:
                tool_output = json.dumps({"error": f"unknown tool: {function_name}"}, ensure_ascii=False)

        except EnrollmentError as e:
            tool_output = json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)
        except Exception as e:
            print(f"Tool Execution Error ({function_name}): {e}")
            import traceback
            traceback.print_exc()
            tool_output = json.dumps({"status": "error", "message": f"Server Error: {str(e)}"}, ensure_ascii=False)

        print(f"Tool Output ({function_name}): {tool_output}")
        return tool_output

    def _fallback_enroll_if_needed(self, user_id: str, message: str) -> Optional[str]:
        normalized_message = message.replace(" ", "").lower()
        enroll_intent_keywords = ["수강신청", "신청해", "신청", "등록해", "등록"]
        has_enroll_intent = any(k in normalized_message for k in enroll_intent_keywords)
        if not has_enroll_intent:
            return None

        print("Tool Call (fallback): list_courses, Args: {}")
        courses = self.course_service.get_all_courses() # Fallback에서는 전체 검색 후 매칭 시도
        # 필터링 적용 여부는 고민이나, 일단 매칭된 강의가 신청 가능한지는 서비스에서 체크할 것임
        
        print(f"Tool Output (fallback:list_courses): {len(courses)} courses")

        if not courses:
            return "현재 신청 가능한 강의가 없습니다."

        matched_course = None
        for course in courses:
            title_no_space = (course.title or "").replace(" ", "").lower()
            if title_no_space and (title_no_space in normalized_message or normalized_message in title_no_space):
                matched_course = course
                break

        if not matched_course:
            course_names = ", ".join([c.title for c in courses[:5]])
            return f"신청할 강의를 정확히 찾지 못했습니다. 가능한 강의 예시는 다음과 같습니다: {course_names}"

        print(f"Tool Call (fallback): enroll_course, Args: {{'course_id': '{matched_course.id}'}}")
        try:
            result = self.enrollment_service.enroll_student(user_id, matched_course.id)
            print(f"Tool Output (fallback:enroll_course): success enrollment_id={result.id}")
            return f"'{matched_course.title}' 수강 신청이 완료되었습니다."
        except EnrollmentError as e:
            print(f"Tool Output (fallback:enroll_course): error={str(e)}")
            return f"수강 신청에 실패했습니다: {str(e)}"
        except Exception as e:
            print(f"Tool Output (fallback:enroll_course): server_error={str(e)}")
            return f"수강 신청 처리 중 서버 오류가 발생했습니다: {str(e)}"

    def _filter_available_courses(self, user_id: str, all_courses: List[Course]) -> List[Course]:
        """
        사용자의 수강 내역을 조회하고,
        1. 이미 수강 중인 강의 제외
        2. 시간이 겹치는 강의 제외 (요일/시간 포맷: 'Mon 09:00', 'Tue 14:00' 등 가정)
        """
        my_enrollments = self.enrollment_service.get_student_enrollments(user_id)
        if not my_enrollments:
            return all_courses

        my_course_ids = {e.course_id for e in my_enrollments}
        course_map = {c.id: c for c in all_courses}
        
        # 내가 수강 중인 강의 상세 정보
        my_courses_details = [course_map[cid] for cid in my_course_ids if cid in course_map]

        available = []
        for candidate in all_courses:
            # 1. 이미 수강 중
            if candidate.id in my_course_ids:
                continue
            
            # 2. 시간 중복 체크
            is_overlap = False
            for my_c in my_courses_details:
                if self._check_time_overlap(candidate, my_c):
                    is_overlap = True
                    break
            
            if not is_overlap:
                available.append(candidate)
        
        return available

    def _check_time_overlap(self, c1: Course, c2: Course) -> bool:
        """
        두 강의 시간 겹침 확인.
        지원 형식:
        1) "HH:MM" (예: "09:00")
        2) "Mon HH:MM" (예: "Mon 09:00")
        """
        if not c1.start_time or not c1.end_time or not c2.start_time or not c2.end_time:
            return False

        try:
            day_map = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}

            def parse_time(value: str):
                parts = value.strip().split()

                # Case 1: HH:MM
                if len(parts) == 1:
                    day = None
                    hhmm = parts[0]
                # Case 2: Day HH:MM
                elif len(parts) == 2:
                    day_key = parts[0].capitalize()
                    if day_key not in day_map:
                        return None, None
                    day = day_map[day_key]
                    hhmm = parts[1]
                else:
                    return None, None

                hh, mm = map(int, hhmm.split(":"))
                return day, hh * 60 + mm

            day1_s, start1 = parse_time(c1.start_time)
            day1_e, end1 = parse_time(c1.end_time)
            day2_s, start2 = parse_time(c2.start_time)
            day2_e, end2 = parse_time(c2.end_time)

            if None in (start1, end1, start2, end2):
                return False

            # Day 정보가 모두 있을 때만 요일 불일치 시 non-overlap 처리
            if day1_s is not None and day2_s is not None and day1_s != day2_s:
                return False
            if day1_e is not None and day2_e is not None and day1_e != day2_e:
                return False

            is_overlapping = (start1 < end2) and (end1 > start2)
            if is_overlapping:
                print(f"Overlap detected: {c1.title} overlaps with {c2.title}")
            return is_overlapping

        except Exception as e:
            print(f"Time overlap check error: {e}")
            return False
