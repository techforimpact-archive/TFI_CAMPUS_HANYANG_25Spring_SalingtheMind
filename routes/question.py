from flask_cors import cross_origin

@question_bp.route('/question/help', methods=['POST', 'OPTIONS'])
@cross_origin(origins='http://localhost:3000')  # 또는 '*'
@token_required
def help_question():
    if request.method == 'OPTIONS':
        return '', 204  # Preflight 요청 응답

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
