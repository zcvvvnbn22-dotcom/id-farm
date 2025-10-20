# barotem_final_complete.py
import time
import random
import os
from playwright.sync_api import sync_playwright

ITEMS = [
    {
        "folder": "상품1",
        "title_file": "제목.txt",
        "desc_file": "설명.txt",
        "price": "28000",
    },
    {
        "folder": "상품2",
        "title_file": "제목.txt",
        "desc_file": "설명.txt",
        "price": "13800",
    },
]

COMMON_CONFIG = {
    "game": "리그오브레전드",
    "server": "서버전체",
    "category": "계정",
    "job": "리그오브레전드",
    "account_type": "게임사",
    "purchase_route": "본인(1대)",
    "payment_history": "결제내역 X",
    "double_auth": "이중연동 X",
    "blind": True,
}


def human_delay(mean=1.0, std_dev=0.3):
    delay = max(0.5, random.gauss(mean, std_dev))
    time.sleep(delay)


def safe_select(page, selector, value):
    try:
        select = page.locator(selector)
        select.wait_for(state="visible", timeout=5000)
        select.scroll_into_view_if_needed()
        human_delay(0.3, 0.1)
        select.select_option(label=value)
        return True
    except:
        return False


def register_item(page, item_data, config, item_number, total):
    """상품 등록"""

    print(f"\n{'=' * 60}")
    print(f"📦 상품 {item_number}/{total}")
    print("=" * 60)

    try:
        folder = item_data["folder"]
        title_path = os.path.join(folder, item_data["title_file"])
        desc_path = os.path.join(folder, item_data["desc_file"])

        with open(title_path, 'r', encoding='utf-8') as f:
            title = f.read().strip()
        with open(desc_path, 'r', encoding='utf-8') as f:
            description = f.read().strip()

        price = item_data["price"]

        print(f"  제목: {title[:40]}...")
        print(f"  가격: {price}원")
        print(f"  설명: {len(description)}자\n")

    except FileNotFoundError as e:
        print(f"❌ 파일 없음: {e}")
        return False

    try:
        # 판매등록 페이지로 이동
        page.goto("https://idfarm.co.kr/", wait_until="domcontentloaded")
        time.sleep(1)
        page.get_by_role("link", name="판매등록").click()
        time.sleep(2)

        print("  [1/10] 게임...")
        search_box = page.get_by_role("textbox", name="검색어를 입력해주세요")
        search_box.click()
        search_box.fill(config["game"])
        search_box.press("Enter")
        time.sleep(3)

        for selector_func in [
            lambda: page.locator("#game_r_sub").get_by_text(config["game"]),
            lambda: page.get_by_text(config["game"]).last,
        ]:
            try:
                element = selector_func()
                element.wait_for(state="visible", timeout=2000)
                element.click()
                break
            except:
                continue

        print("  [2/10] 서버...")
        page.get_by_text(config["server"], exact=True).click()
        human_delay(1.0, 0.2)

        print("  [3/10] 카테고리...")
        page.locator('label[for="character"]').click()
        human_delay(1.5, 0.3)

        print("  [4/10] 상세정보...")
        time.sleep(2)
        safe_select(page, 'select[name="jobCdIdx"]', config["job"])
        safe_select(page, 'select[name="accntKind"]', config["account_type"])
        safe_select(page, 'select[name="prchsRoute"]', config["purchase_route"])
        safe_select(page, 'select[name="customerNumberYn"]', config["payment_history"])
        safe_select(page, 'select[name="2certYn"]', config["double_auth"])

        print("  [5/10] 제목...")
        title_input = page.locator('input[name="subject"]')
        title_input.wait_for(state="visible", timeout=10000)
        title_input.click()
        human_delay(0.3, 0.1)
        title_input.fill(title)

        print("  [6/10] 가격...")
        price_input = page.locator('input[name="salePrice"]')
        price_input.click()
        human_delay(0.3, 0.1)
        price_input.fill(price)

        print("  [7/10] 흥정불가...")
        try:
            nego_label = page.locator('label[for="nego_no"]')
            nego_label.click(force=True)
        except:
            pass

        # === 8단계: 설명 입력 (수정됨!) ===
            # barotem_final_ultimate.py
            # ... (전체 코드 동일, 8단계만 교체) ...

            # === 8단계: 설명 입력 (최종 버전!) ===
            print("  [8/10] 설명 입력...")
            page.evaluate("window.scrollBy(0, 600)")
            time.sleep(2)

            desc_success = False

            try:
                print("       → textarea 활성화...")

                # 1. textarea를 강제로 보이게 만들기
                page.evaluate('''
                        const ta = document.querySelector('textarea[name="wr_content"]');
                        if (ta) {
                            ta.style.display = 'block';
                            ta.style.visibility = 'visible';
                            ta.style.opacity = '1';
                            ta.style.position = 'relative';
                        }
                    ''')
                time.sleep(0.5)

                textarea = page.locator('textarea[name="wr_content"]')

                print("       → 클릭...")
                textarea.click(timeout=3000)
                time.sleep(0.5)

                print("       → 포커스...")
                textarea.focus()
                time.sleep(0.3)

                print("       → 기존 내용 지우기...")
                page.keyboard.press("Control+A")
                time.sleep(0.1)
                page.keyboard.press("Delete")
                time.sleep(0.3)

                print(f"       → 키보드로 타이핑 ({len(description)}자)...")

                # page.keyboard로 직접 타이핑
                for i, char in enumerate(description):
                    page.keyboard.type(char, delay=10)
                    if (i + 1) % 50 == 0:
                        print(f"          {i + 1}/{len(description)}...")

                time.sleep(1)

                # 확인
                value = textarea.input_value()
                print(f"       → 입력 확인: {len(value)}자")

                if len(value) > 10:
                    print(f"       ✅ 타이핑 성공!")
                    desc_success = True
                else:
                    print(f"       ⚠️ 타이핑 실패")

            except Exception as e:
                print(f"       ❌ 타이핑 실패: {str(e)[:60]}")

            # 백업: 수동 입력
            if not desc_success:
                print("\n       " + "=" * 50)
                print("       ⚠️ 자동 입력 실패!")
                print("       " + "=" * 50)
                print("       브라우저에서 설명란을 찾아 직접 입력해주세요")
                print(f"\n       내용:\n{description}\n")
                print("       " + "=" * 50)
                input("\n       입력 완료 후 Enter ▶ ")

        print("  [9/10] 블라인드...")
        if config["blind"]:
            try:
                blind_cb = page.locator('input#blind')
                is_checked = blind_cb.is_checked()

                if not is_checked:
                    blind_label = page.locator('label[for="blind"]')
                    blind_label.scroll_into_view_if_needed()
                    blind_label.click()
                    time.sleep(0.3)
            except:
                pass

        print("  [10/10] 등록...")
        time.sleep(2)

        submit_btn = page.locator('button:has-text("물품등록")')
        if submit_btn.count() > 0:
            submit_btn.first.scroll_into_view_if_needed()
            human_delay(0.5, 0.2)
            submit_btn.first.click()
            print("       ⏳ 처리중...")
            time.sleep(5)
            print("       ✅ 완료!")
            return True
        else:
            print("       ❌ 등록버튼 없음")
            return False

    except Exception as e:
        print(f"  ❌ 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


# --- 메인 실행 ---
try:
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir="./my_chrome_profile",
            headless=False,
        )

        page = context.pages[0] if context.pages else context.new_page()

        # 로그인 확인
        print("\n🔐 로그인 확인...")
        page.goto("https://idfarm.co.kr/", wait_until="domcontentloaded")
        time.sleep(2)

        try:
            page.wait_for_selector('a:has-text("로그아웃")', timeout=5000)
            print("✅ 자동 로그인 성공!\n")
        except:
            print("\n⚠️ 로그인 필요")
            page.goto("https://idfarm.co.kr/login")
            input("로그인 후 Enter ▶ ")
            page.goto("https://idfarm.co.kr/")
            print("✅ 로그인 완료\n")

        # 여러 상품 등록
        print("=" * 60)
        print(f"🚀 총 {len(ITEMS)}개 상품 자동 등록 시작")
        print("=" * 60)

        success = 0
        fail = 0

        for i, item in enumerate(ITEMS, 1):
            if register_item(page, item, COMMON_CONFIG, i, len(ITEMS)):
                success += 1
            else:
                fail += 1
                response = input("\n계속? (y/n): ")
                if response.lower() != 'y':
                    break

            if i < len(ITEMS):
                print(f"\n⏳ 다음 상품까지 5초 대기...\n")
                time.sleep(5)

        print("\n" + "=" * 60)
        print("📊 최종 결과")
        print("=" * 60)
        print(f"  ✅ 성공: {success}개")
        print(f"  ❌ 실패: {fail}개")
        print("=" * 60)

        print("\n30초 후 종료...")
        page.wait_for_timeout(30000)
        context.close()
        print("\n👋 프로그램 종료")

except KeyboardInterrupt:
    print("\n⚠️  사용자가 중단했습니다")
except Exception as e:
    print(f"\n❌ 오류: {e}")
    import traceback

    traceback.print_exc()