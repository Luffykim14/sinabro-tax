# 🧾 시나브로마케팅 세금계산서 자동 입력 프로그램

거래명세서 이미지를 업로드하면 국세청 전자세금계산서 일괄발급 엑셀 양식을 자동으로 채워주는 프로그램입니다.

---

## ⚙️ 최초 설치 (처음 한 번만)

### 1. Python 설치 확인
```cmd
python --version
```
Python 3.9 이상이어야 합니다. 없으면 https://www.python.org 에서 설치.

### 2. 필요 패키지 설치
```cmd
cd tax_auto
pip install -r requirements.txt
```

### 3. Anthropic API 키 설정
```cmd
set ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxx
```
> API 키는 https://console.anthropic.com 에서 발급받으세요.
> 매번 입력하기 귀찮으면 윈도우 환경변수에 영구 등록하세요.

---

## 🚀 실행 방법

```cmd
cd tax_auto
python app.py
```

브라우저에서 **http://localhost:5000** 을 열면 됩니다.

---

## 📋 사용 방법

1. 거래명세서 이미지(PNG/JPG)를 업로드 영역에 드래그하거나 파일 선택
2. AI가 자동으로 데이터를 파싱합니다 (10~20초 소요)
3. 파싱된 결과를 확인하고 필요시 수정
4. **엑셀 다운로드** 버튼 클릭
5. 다운로드된 파일을 국세청 홈택스에 업로드

---

## 📁 파일 구조

```
tax_auto/
├── app.py              # Flask 메인 서버
├── parser.py           # Claude Vision API 파싱
├── excel_writer.py     # 엑셀 파일 생성
├── requirements.txt    # 필요 패키지
├── README.md           # 이 파일
├── templates/
│   └── index.html      # 웹 UI
├── uploads/            # 업로드 임시 저장 (자동 생성)
└── outputs/            # 엑셀 출력 파일 (자동 생성)
```

---

## 🔧 고정 정보 (공급자 - 시나브로마케팅)

| 항목 | 값 |
|------|-----|
| 상호 | 시나브로마케팅 |
| 대표자 | 김수현 |
| 등록번호 | 711-18-02350 |
| 주소 | 서울특별시 강동구 천호대로 505, 9층 |
| 업태/종목 | 서비스업/광고대행업 |
| 이메일 | info@sinabro.biz |

공급자 정보는 `excel_writer.py`의 `SUPPLIER` 딕셔너리에서 수정할 수 있습니다.

---

## ❓ 자주 묻는 문제

**Q. 파싱이 안 돼요**  
A. ANTHROPIC_API_KEY 환경변수가 설정되어 있는지 확인하세요.

**Q. 날짜가 오늘 날짜로 들어가요**  
A. 파일명에 날짜를 포함해주세요. 예: `0502_물티슈_113건.png`

**Q. 데이터가 틀려요**  
A. 결과 화면에서 직접 수정 후 다운로드하세요.
