from flask import Blueprint, request, Response
import openai
import json
from flasgger import swag_from

question_bp = Blueprint('question', __name__)

# 한글 JSON 응답 함수
def json_kor(data, status=200):
    return Response(
        json.dumps(data, ensure_ascii=False, default=str),
        content_type="application/json; charset=utf-8",
        status=status
    )

@question_bp.route('/question/generate', methods=['POST'])
@swag_from({
    'tags': ['Question'],
    'requestBody': {
        'required': True,
        'content': {
            'application/json': {
                'schema': {
                    'type': 'object',
                    'properties': {
                        'emotion': {
                            'type': 'string',
                            'example': '불안'
                        }
                    },
                    'required': ['emotion']
                }
            }
        }
    },
    'responses': {
        200: {
            'description': '감정 기반 질문 생성 성공',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'question': {
                                'type': 'string',
                                'example': '불안한 마음이 들 때, 당신은 어떤 상황을 가장 먼저 떠올리게 되나요?'
                            }
                        }
                    }
                }
            }
        },
        400: {'description': '감정 누락 오류'},
        500: {'description': 'OpenAI API 오류'}
    }
})
def generate_question():
    """
    감정을 기반으로 글쓰기를 유도하는 질문 생성
    """
    data = request.json
    emotion = data.get("emotion")

    if not emotion:
        return json_kor({"error": "emotion 필드는 필수입니다."}), 400

    prompt = f'''
    사용자가 "{emotion}"이라는 감정을 선택했습니다.
    이 감정에 어울리는, 글쓰기를 시작하게 도와줄 따뜻하고 구체적인 질문 한 가지를 만들어주세요.
    '''

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        question = response.choices[0].message.content.strip()
        return json_kor({"question": question}), 200
    except Exception as e:
        return json_kor({"error": str(e)}), 500


@question_bp.route('/question/help', methods=['POST'])
@swag_from({
    'tags': ['Question'],
    'requestBody': {
        'required': True,
        'content': {
            'application/json': {
                'schema': {
                    'type': 'object',
                    'properties': {
                        'partial_letter': {
                            'type': 'string',
                            'example': '요즘 학교생활이 너무 힘들어요. 친구들이 저를 피하는 것 같고...'
                        }
                    },
                    'required': ['partial_letter']
                }
            }
        }
    },
    'responses': {
        200: {
            'description': '글쓰기 도움 질문 생성 성공',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'help_question': {
                                'type': 'string',
                                'example': '그런 상황이 반복될 때, 당신은 어떤 감정을 가장 먼저 느끼나요?'
                            }
                        }
                    }
                }
            }
        },
        400: {'description': '입력값 누락'},
        500: {'description': 'OpenAI API 오류'}
    }
})
def help_question():
    """
    편지 작성 중 막혔을 때 글쓰기를 도와주는 질문 생성
    """
    data = request.json
    partial_letter = data.get("partial_letter", "").strip()

    if not partial_letter:
        return json_kor({"error": "partial_letter는 필수입니다."}), 400

    prompt = f"""
    사용자가 편지를 쓰다가 막혔습니다.
    지금까지 작성한 내용은 다음과 같습니다:

    "{partial_letter}"

    이 내용을 바탕으로, 사용자가 글을 자연스럽게 이어서 쓸 수 있도록 도와주는 따뜻한 질문을 한 문장만 작성해주세요.
    온기라는 가상의 캐릭터가 말을 거는 느낌으로 작성해주세요.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        help_q = response.choices[0].message.content.strip()
        return json_kor({"help_question": help_q}), 200
    except Exception as e:
        return json_kor({"error": str(e)}), 500