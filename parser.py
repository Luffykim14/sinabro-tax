"""
거래명세서 이미지 파싱 모듈
Claude Vision API를 사용하여 이미지에서 세금계산서 데이터 추출
"""

import anthropic
import json
import re


def parse_image_with_claude(base64_image: str, media_type: str, filename: str) -> dict:
    """
    Claude Vision API로 거래명세서 이미지 파싱
    """
    client = anthropic.Anthropic()

    prompt = """이 거래명세서 이미지에서 데이터를 추출하세요.

반드시 아래 JSON 형식으로만 응답하세요. 다른 텍스트 절대 금지.

{
  "supplier_info": {
    "registration_number": "공급받는자 사업자등록번호 (하이픈 없이)",
    "company_name": "공급받는자 상호",
    "representative": "공급받는자 대표자명",
    "address": "공급받는자 주소",
    "business_type": "공급받는자 업태",
    "business_item": "공급받는자 종목",
    "email": "공급받는자 이메일 (없으면 빈 문자열)"
  },
  "totals": {
    "supply_amount": 총합계금액(숫자),
    "tax_amount": 총부가세합계(숫자)
  },
  "items": [
    {
      "name": "품목명 그대로",
      "quantity": 수량(숫자),
      "unit_price": 단가(숫자),
      "supply_amount": 금액(숫자),
      "tax_amount": 부가세(숫자)
    }
  ]
}

규칙:
- 표에 데이터가 있는 모든 행 포함 (빈 행 제외)
- "실행비용" 이라고 적힌 행은 반드시 name을 정확히 "실행비용" 으로 입력
- 숫자는 쉼표 없이 순수 숫자만
- JSON만 출력, 설명 절대 금지"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": base64_image,
                        },
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ],
            }
        ],
    )

    response_text = message.content[0].text.strip()

    # JSON 파싱
    try:
        response_text = re.sub(r'```json\s*', '', response_text)
        response_text = re.sub(r'```\s*', '', response_text)
        data = json.loads(response_text)
    except json.JSONDecodeError:
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
        else:
            data = {
                "supplier_info": {
                    "registration_number": "",
                    "company_name": "",
                    "representative": "",
                    "address": "",
                    "business_type": "",
                    "business_item": "",
                    "email": ""
                },
                "totals": {"supply_amount": 0, "tax_amount": 0},
                "items": []
            }

    # ===== 품목 정리: 제품비 합산 + 실행비용 분리 =====
    items = data.get('items', [])

    product_supply = 0
    product_tax = 0
    product_qty = 0
    exec_supply = 0
    exec_tax = 0
    exec_qty = 0
    exec_unit_price = 0

    for item in items:
        name = item.get('name', '').strip()
        # 실행비용 감지: 이름에 '실행' 포함
        if '실행' in name:
            exec_supply += item.get('supply_amount', 0)
            exec_tax += item.get('tax_amount', 0)
            exec_qty += item.get('quantity', 0)
            exec_unit_price = item.get('unit_price', 0)
        else:
            product_supply += item.get('supply_amount', 0)
            product_tax += item.get('tax_amount', 0)
            product_qty += item.get('quantity', 0)

    # 제품비 단가: 공급가액 / 수량 (반올림)
    product_unit_price = round(product_supply / product_qty) if product_qty else 0

    data['items'] = [
        {
            'name': '제품비',
            'quantity': product_qty,
            'unit_price': product_unit_price,
            'supply_amount': product_supply,
            'tax_amount': product_tax
        },
        {
            'name': '실행비용',
            'quantity': exec_qty,
            'unit_price': exec_unit_price,
            'supply_amount': exec_supply,
            'tax_amount': exec_tax
        }
    ]

    return data
