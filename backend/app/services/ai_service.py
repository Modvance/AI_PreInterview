"""
AI Service - Provides LLM, ASR, TTS capabilities using DashScope SDK
"""
import os
import json
import base64
import asyncio
import threading
from typing import Optional, List, Callable
from http import HTTPStatus

import dashscope
from dashscope import Generation
from dashscope.audio.qwen_tts_realtime import QwenTtsRealtime, QwenTtsRealtimeCallback, AudioFormat
from dashscope.audio.qwen_omni import OmniRealtimeConversation, OmniRealtimeCallback, MultiModality
from dashscope.audio.qwen_omni.omni_realtime import TranscriptionParams

from ..core.config import get_settings
from ..schemas.interview import (
    Question, AnswerEvaluation, InterviewReport, 
    QuestionReport, AnswerRecord
)


class AIService:
    """AI service wrapper using DashScope SDK for LLM, ASR, TTS"""
    
    def __init__(self):
        self.settings = get_settings()
        self._init_dashscope()
    
    def _init_dashscope(self):
        """Initialize DashScope API key"""
        # Priority: llm_api_key > DASHSCOPE_API_KEY env var
        api_key = self.settings.llm_api_key or os.environ.get('DASHSCOPE_API_KEY')
        if api_key:
            dashscope.api_key = api_key
    
    def _get_api_key(self, service: str = "llm") -> Optional[str]:
        """Get API key for specific service"""
        if service == "asr":
            return self.settings.asr_api_key or self.settings.llm_api_key or os.environ.get('DASHSCOPE_API_KEY')
        elif service == "tts":
            return self.settings.tts_api_key or self.settings.llm_api_key or os.environ.get('DASHSCOPE_API_KEY')
        else:
            return self.settings.llm_api_key or os.environ.get('DASHSCOPE_API_KEY')
    
    # ============ LLM Service ============
    
    def _call_llm(
        self,
        messages: List[dict],
        response_format: Optional[dict] = None,
        stream: bool = False
    ):
        """
        Call LLM using DashScope Generation API
        
        Args:
            messages: Chat messages
            response_format: Response format (e.g., {'type': 'json_object'})
            stream: Whether to use streaming
        
        Returns:
            Response object or generator for streaming
        """
        kwargs = {
            "model": self.settings.llm_model,
            "messages": messages,
            "result_format": "message",
        }
        
        if response_format:
            kwargs["response_format"] = response_format
        
        if stream:
            kwargs["stream"] = True
            kwargs["incremental_output"] = True
        
        return Generation.call(**kwargs)
    
    async def evaluate_answer(
        self,
        question: Question,
        selected_option: Optional[str],
        explanation: str
    ) -> AnswerEvaluation:
        """
        Evaluate user's answer using LLM
        
        Args:
            question: The question
            selected_option: User's selected option
            explanation: User's explanation of solution approach
        
        Returns:
            Evaluation result
        """
        # Check if answer is correct
        is_correct = selected_option == question.correct_answer if selected_option else False
        
        if not self._get_api_key("llm"):
            # Fallback to rule-based evaluation if no API key
            return self._rule_based_evaluation(question, selected_option, explanation, is_correct)
        
        # Build evaluation prompt
        prompt = self._build_evaluation_prompt(question, selected_option, explanation)
        
        messages = [
            {
                "role": "system", 
                "content": "You are a professional technical interviewer responsible for evaluating candidates' answers and problem-solving approaches. Please provide objective and professional feedback in Chinese."
            },
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self._call_llm(
                messages=messages,
                response_format={"type": "json_object"}
            )
            
            if response.status_code == HTTPStatus.OK:
                content = response.output.choices[0].message.content
                result = json.loads(content)
                return AnswerEvaluation(
                    is_correct=is_correct,
                    score=result.get("score", 60 if is_correct else 30),
                    feedback=result.get("feedback", ""),
                    hints=result.get("hints", []),
                    key_points_hit=result.get("key_points_hit", []),
                    key_points_missed=result.get("key_points_missed", [])
                )
            else:
                print(f"LLM evaluation failed: {response.code} - {response.message}")
        except Exception as e:
            print(f"LLM evaluation error: {e}")
        
        # Fallback to rule-based evaluation
        return self._rule_based_evaluation(question, selected_option, explanation, is_correct)
    
    def _build_evaluation_prompt(
        self,
        question: Question,
        selected_option: Optional[str],
        explanation: str
    ) -> str:
        """Build evaluation prompt"""
        options_text = ""
        if question.options:
            options_text = "\n".join([f"{o.key}. {o.content}" for o in question.options])
        
        return f"""Please evaluate the following interview answer:

## Question
{question.title}

{question.content}

Options:
{options_text}

Correct Answer: {question.correct_answer}
Answer Explanation: {question.explanation}
Key Points: {', '.join(question.key_points)}

## Candidate's Answer
Selected Option: {selected_option or "Not selected"}
Problem-solving Approach: {explanation}

## Please output JSON format evaluation result (respond in Chinese)
{{
    "score": 0-100 score,
    "feedback": "Feedback for the candidate, friendly and professional tone, point out errors if any, acknowledge good approaches",
    "hints": ["Hints if candidate is stuck or has wrong approach"],
    "key_points_hit": ["Key points the candidate mentioned or got right"],
    "key_points_missed": ["Key points the candidate missed"]
}}"""
    
    def _rule_based_evaluation(
        self,
        question: Question,
        selected_option: Optional[str],
        explanation: str,
        is_correct: bool
    ) -> AnswerEvaluation:
        """Rule-based evaluation (fallback when LLM unavailable)"""
        score = 0
        feedback = ""
        hints = []
        key_points_hit = []
        key_points_missed = question.key_points.copy()
        
        if is_correct:
            score = 70
            feedback = "Correct answer!"
            
            for point in question.key_points:
                if point.lower() in explanation.lower():
                    key_points_hit.append(point)
                    key_points_missed.remove(point)
                    score += 10
            
            if key_points_hit:
                feedback += f" Your approach mentioned {', '.join(key_points_hit)}, well done!"
            
            if key_points_missed:
                feedback += f" You could also consider {', '.join(key_points_missed)}."
            
            score = min(score, 100)
        else:
            score = 30
            feedback = f"Not quite right. The correct answer is {question.correct_answer}."
            
            for point in question.key_points:
                if point.lower() in explanation.lower():
                    key_points_hit.append(point)
                    key_points_missed.remove(point)
                    score += 5
            
            if key_points_hit:
                feedback += f" However, you mentioned {', '.join(key_points_hit)}, showing the right direction."
            
            hints.append(question.explanation[:100] + "...")
        
        return AnswerEvaluation(
            is_correct=is_correct,
            score=score,
            feedback=feedback,
            hints=hints,
            key_points_hit=key_points_hit,
            key_points_missed=key_points_missed
        )
    
    async def generate_interview_feedback(
        self,
        question: Question,
        evaluation: AnswerEvaluation
    ) -> str:
        """
        Generate interviewer's verbal feedback using LLM
        
        Args:
            question: The question
            evaluation: Evaluation result
        
        Returns:
            Conversational feedback text
        """
        if not self._get_api_key("llm"):
            return evaluation.feedback
        
        messages = [
            {
                "role": "system", 
                "content": "You are a friendly and professional technical interviewer. Respond in Chinese."
            },
            {
                "role": "user", 
                "content": f"""As an interviewer, please generate a conversational feedback based on the following evaluation result.
Requirements:
1. Friendly and professional tone
2. Acknowledge if correct
3. Gently point out and guide if incorrect
4. Keep within 100 characters
5. Respond in Chinese

Evaluation Result:
- Answer Correct: {evaluation.is_correct}
- Score: {evaluation.score}
- Key Points Hit: {evaluation.key_points_hit}
- Key Points Missed: {evaluation.key_points_missed}

Please output the feedback text directly, no other formatting."""
            }
        ]
        
        try:
            response = self._call_llm(messages=messages)
            
            if response.status_code == HTTPStatus.OK:
                return response.output.choices[0].message.content.strip()
        except Exception as e:
            print(f"Generate feedback error: {e}")
        
        return evaluation.feedback
    
    async def generate_report(
        self,
        session_id: str,
        candidate_name: Optional[str],
        position: Optional[str],
        questions: List[Question],
        answers: List[AnswerRecord],
        duration: int
    ) -> InterviewReport:
        """
        Generate interview report
        
        Args:
            session_id: Session ID
            candidate_name: Candidate name
            position: Applied position
            questions: Question list
            answers: Answer records
            duration: Interview duration (seconds)
        
        Returns:
            Interview report
        """
        from datetime import datetime
        
        # Calculate basic statistics
        total_score = 0
        correct_count = 0
        question_reports = []
        
        question_map = {q.id: q for q in questions}
        
        for answer in answers:
            q = question_map.get(answer.question_id)
            if not q:
                continue
            
            total_score += answer.evaluation.score
            if answer.evaluation.is_correct:
                correct_count += 1
            
            question_reports.append(QuestionReport(
                question_title=q.title,
                question_type=q.type,
                difficulty=q.difficulty,
                is_correct=answer.evaluation.is_correct,
                score=answer.evaluation.score,
                candidate_answer=f"{answer.selected_option}: {answer.explanation[:50]}...",
                correct_answer=q.correct_answer,
                evaluation_summary=answer.evaluation.feedback[:100]
            ))
        
        total_questions = len(answers)
        avg_score = total_score // total_questions if total_questions > 0 else 0
        
        # Generate detailed analysis using LLM
        strengths, weaknesses, overall_comment, recommendation = await self._generate_report_analysis(
            questions, answers, avg_score, correct_count, total_questions
        )
        
        return InterviewReport(
            session_id=session_id,
            candidate_name=candidate_name,
            position=position,
            total_score=avg_score,
            total_questions=total_questions,
            correct_count=correct_count,
            logic_ability=avg_score,
            expression_ability=min(avg_score + 10, 100),
            problem_solving=avg_score,
            question_reports=question_reports,
            strengths=strengths,
            weaknesses=weaknesses,
            overall_comment=overall_comment,
            recommendation=recommendation,
            interview_duration=duration,
            created_at=datetime.now()
        )
    
    async def _generate_report_analysis(
        self,
        questions: List[Question],
        answers: List[AnswerRecord],
        avg_score: int,
        correct_count: int,
        total_questions: int
    ) -> tuple:
        """Generate report analysis content using LLM"""
        if not self._get_api_key("llm"):
            return self._rule_based_report_analysis(avg_score, correct_count, total_questions)
        
        # Build analysis prompt
        answers_summary = []
        for i, (q, a) in enumerate(zip(questions, answers)):
            status = "Correct" if a.evaluation.is_correct else "Incorrect"
            answers_summary.append(f"Question {i+1} ({q.type.value}): Score {a.evaluation.score}, {status}")
        
        messages = [
            {
                "role": "system", 
                "content": "You are a professional recruitment consultant. Please objectively analyze candidate performance. Respond in Chinese."
            },
            {
                "role": "user", 
                "content": f"""Please analyze the following interview results and generate report content (respond in Chinese):

Interview Summary:
- Total Questions: {total_questions}
- Correct Answers: {correct_count}
- Average Score: {avg_score}

Question Details:
{chr(10).join(answers_summary)}

Please output in JSON format:
{{
    "strengths": ["2-3 candidate strengths"],
    "weaknesses": ["1-2 areas for improvement"],
    "overall_comment": "Overall evaluation within 100 characters",
    "recommendation": "Recommendation for the hiring team, such as whether to proceed to next round"
}}"""
            }
        ]
        
        try:
            response = self._call_llm(
                messages=messages,
                response_format={"type": "json_object"}
            )
            
            if response.status_code == HTTPStatus.OK:
                content = response.output.choices[0].message.content
                result = json.loads(content)
                return (
                    result.get("strengths", []),
                    result.get("weaknesses", []),
                    result.get("overall_comment", ""),
                    result.get("recommendation", "")
                )
        except Exception as e:
            print(f"Generate report analysis error: {e}")
        
        return self._rule_based_report_analysis(avg_score, correct_count, total_questions)
    
    def _rule_based_report_analysis(
        self,
        avg_score: int,
        correct_count: int,
        total_questions: int
    ) -> tuple:
        """Rule-based report analysis"""
        strengths = []
        weaknesses = []
        
        if avg_score >= 80:
            strengths.append("Strong logical thinking ability")
            strengths.append("Clear problem-solving approach")
        elif avg_score >= 60:
            strengths.append("Basic logical thinking ability")
        
        if correct_count == total_questions:
            strengths.append("High answer accuracy")
        
        if avg_score < 60:
            weaknesses.append("Logical thinking needs improvement")
        if correct_count < total_questions // 2:
            weaknesses.append("Some questions not fully understood")
        
        if not strengths:
            strengths.append("Serious attitude, actively answered")
        if not weaknesses:
            weaknesses.append("Can further improve problem-solving efficiency")
        
        if avg_score >= 80:
            overall_comment = "Candidate performed excellently with strong logical thinking and clear approach."
            recommendation = "Recommend proceeding to next interview round."
        elif avg_score >= 60:
            overall_comment = "Candidate performed well with basic logical thinking ability."
            recommendation = "Consider next round, but focus on analytical ability."
        else:
            overall_comment = "Candidate's logical thinking needs improvement."
            recommendation = "Recommend postponing next round or arrange supplementary test."
        
        return strengths, weaknesses, overall_comment, recommendation
    
    # ============ ASR Service (Speech to Text) ============
    
    async def speech_to_text(
        self, 
        audio_data: bytes, 
        sample_rate: int = 16000,
        audio_format: str = "pcm",
        language: str = "zh"
    ) -> str:
        """
        Speech to text using DashScope ASR
        
        Args:
            audio_data: Audio data bytes (PCM format recommended)
            sample_rate: Audio sample rate (default 16000)
            audio_format: Audio format (pcm, wav)
            language: Language code (zh, en)
        
        Returns:
            Transcribed text
        """
        api_key = self._get_api_key("asr")
        if not api_key:
            raise ValueError("ASR API key not configured")
        
        # Set API key for this request
        dashscope.api_key = api_key
        
        result_text = ""
        complete_event = asyncio.Event()
        error_message = None
        
        class ASRCallback(OmniRealtimeCallback):
            def __init__(self):
                self.transcripts = []
            
            def on_open(self):
                pass
            
            def on_close(self, code, msg):
                pass
            
            def on_event(self, response):
                nonlocal result_text, error_message
                try:
                    event_type = response.get('type', '')
                    if event_type == 'conversation.item.input_audio_transcription.completed':
                        result_text = response.get('transcript', '')
                        complete_event.set()
                    elif event_type == 'error':
                        error_message = response.get('error', {}).get('message', 'Unknown error')
                        complete_event.set()
                except Exception as e:
                    error_message = str(e)
                    complete_event.set()
        
        callback = ASRCallback()
        
        # Use URL from config
        asr_url = self.settings.asr_api_base
        
        conversation = OmniRealtimeConversation(
            model=self.settings.asr_model,
            url=asr_url,
            callback=callback
        )
        
        try:
            conversation.connect()
            
            transcription_params = TranscriptionParams(
                language=language,
                sample_rate=sample_rate,
                input_audio_format=audio_format
            )
            
            conversation.update_session(
                output_modalities=[MultiModality.TEXT],
                enable_input_audio_transcription=True,
                transcription_params=transcription_params
            )
            
            # Send audio in chunks
            chunk_size = 3200
            for i in range(0, len(audio_data), chunk_size):
                chunk = audio_data[i:i + chunk_size]
                audio_b64 = base64.b64encode(chunk).decode('ascii')
                conversation.append_audio(audio_b64)
                await asyncio.sleep(0.05)
            
            conversation.end_session()
            
            # Wait for completion with timeout
            try:
                await asyncio.wait_for(complete_event.wait(), timeout=30.0)
            except asyncio.TimeoutError:
                raise TimeoutError("ASR processing timeout")
            
            if error_message:
                raise RuntimeError(f"ASR error: {error_message}")
            
            return result_text
            
        finally:
            conversation.close()
    
    # ============ TTS Service (Text to Speech) ============
    
    async def text_to_speech(self, text: str) -> bytes:
        """
        Text to speech using DashScope TTS
        
        Args:
            text: Text content to convert
        
        Returns:
            Audio data bytes (PCM 24kHz format)
        """
        api_key = self._get_api_key("tts")
        if not api_key:
            raise ValueError("TTS API key not configured")
        
        # Set API key for this request
        dashscope.api_key = api_key
        
        audio_chunks = []
        complete_event = threading.Event()
        error_message = None
        
        class TTSCallback(QwenTtsRealtimeCallback):
            def on_open(self):
                pass
            
            def on_close(self, close_status_code, close_msg):
                pass
            
            def on_event(self, response):
                nonlocal error_message
                try:
                    event_type = response.get('type', '')
                    if event_type == 'response.audio.delta':
                        audio_b64 = response.get('delta', '')
                        if audio_b64:
                            audio_chunks.append(base64.b64decode(audio_b64))
                    elif event_type == 'session.finished':
                        complete_event.set()
                    elif event_type == 'error':
                        error_message = response.get('error', {}).get('message', 'Unknown error')
                        complete_event.set()
                except Exception as e:
                    error_message = str(e)
                    complete_event.set()
        
        callback = TTSCallback()
        
        # Use URL from config
        tts_url = self.settings.tts_api_base
        
        tts = QwenTtsRealtime(
            model=self.settings.tts_model,
            callback=callback,
            url=tts_url
        )
        
        try:
            tts.connect()
            tts.update_session(
                voice=self.settings.tts_voice,
                response_format=AudioFormat.PCM_24000HZ_MONO_16BIT,
                mode='server_commit'
            )
            
            # Send text in chunks for better streaming
            chunk_size = 50
            for i in range(0, len(text), chunk_size):
                chunk = text[i:i + chunk_size]
                tts.append_text(chunk)
                await asyncio.sleep(0.05)
            
            tts.finish()
            
            # Wait for completion with timeout
            complete_event.wait(timeout=60.0)
            
            if error_message:
                raise RuntimeError(f"TTS error: {error_message}")
            
            return b''.join(audio_chunks)
            
        finally:
            pass  # Connection will be closed automatically
    
    async def text_to_speech_stream(self, text: str, on_audio_chunk: Callable[[bytes], None]):
        """
        Streaming text to speech for real-time playback
        
        Args:
            text: Text content to convert
            on_audio_chunk: Callback function for each audio chunk
        """
        api_key = self._get_api_key("tts")
        if not api_key:
            raise ValueError("TTS API key not configured")
        
        # Set API key for this request
        dashscope.api_key = api_key
        
        complete_event = threading.Event()
        error_message = None
        
        class TTSStreamCallback(QwenTtsRealtimeCallback):
            def on_open(self):
                pass
            
            def on_close(self, close_status_code, close_msg):
                pass
            
            def on_event(self, response):
                nonlocal error_message
                try:
                    event_type = response.get('type', '')
                    if event_type == 'response.audio.delta':
                        audio_b64 = response.get('delta', '')
                        if audio_b64:
                            on_audio_chunk(base64.b64decode(audio_b64))
                    elif event_type == 'session.finished':
                        complete_event.set()
                    elif event_type == 'error':
                        error_message = response.get('error', {}).get('message', 'Unknown error')
                        complete_event.set()
                except Exception as e:
                    error_message = str(e)
                    complete_event.set()
        
        callback = TTSStreamCallback()
        
        # Use URL from config
        tts_url = self.settings.tts_api_base
        
        tts = QwenTtsRealtime(
            model=self.settings.tts_model,
            callback=callback,
            url=tts_url
        )
        
        try:
            tts.connect()
            tts.update_session(
                voice=self.settings.tts_voice,
                response_format=AudioFormat.PCM_24000HZ_MONO_16BIT,
                mode='server_commit'
            )
            
            # Send text
            tts.append_text(text)
            tts.finish()
            
            # Wait for completion
            complete_event.wait(timeout=60.0)
            
            if error_message:
                raise RuntimeError(f"TTS stream error: {error_message}")
            
        finally:
            pass


# Singleton instance
_ai_service: Optional[AIService] = None


def get_ai_service() -> AIService:
    """Get AI service singleton"""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service
