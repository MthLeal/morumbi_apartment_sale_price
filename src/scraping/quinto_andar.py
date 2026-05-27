import asyncio
import logging
import pandas as pd
import time
import random
from pathlib import Path
from utils.utils import save_data, normalize_url_text
from playwright.async_api import async_playwright, Playwright, TimeoutError, Page, Response
from playwright_stealth import Stealth

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

output_path_name = Path(__file__).parent.parent.parent / 'data' / 'house_data.parquet'
districts_url = 'https://www.quintoandar.com.br/'

async def run_spider(pw: Playwright, districts: list[str]) -> pd.DataFrame:
    data = pd.DataFrame(columns=[
        'id',
        'total',
        'area',
        'bedroom_qtd',
        'garage',
        'address',
        'state'
    ])

    try:
        browser = await pw.chromium.launch(headless=False)
        context = await browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36')

        # abre o navegador e a pagina
        page = await context.new_page()

        temp_data = pd.DataFrame(columns=[
            'id',
            'total',
            'area',
            'bedroom_qtd',
            'garage',
            'address',
            'state'
        ])
        for district in districts:
            wait_time = random.randint(3, 8)
            time.sleep(wait_time)
            response = await page.goto(f'https://www.quintoandar.com.br/comprar/imovel/{district}-sao-paulo-sp-brasil/apartamento')

            if not response.ok:
                logging.error(f'Requisition Error on trying to achieve district {district}: {response.status} {response.headers}')
            else:
                try:
                    count_clicks = 0
                    number_elements_before = await page.get_by_test_id("house-card-container").count()
                    while count_clicks < 25:
                        botao_carregar_mais = page.get_by_test_id("load-more-button")

                        try:
                            await botao_carregar_mais.wait_for(
                                state='visible',
                                timeout=5000
                            )
                            number_elements_before = await page.get_by_test_id("house-card-container").count()
                            await botao_carregar_mais.click()
                            count_clicks += 1

                        except TimeoutError:
                            break
                    
                    await page.wait_for_function(f"document.querySelectorAll('[data-testid=\"house-card-container\"]').length > {number_elements_before}")

                    locator_links = await page.get_by_test_id("HOUSE_CARDS_GRID_TEST_ID").get_by_test_id('house-card-container').get_by_role('link').evaluate_all('els => els.map(el => el.href)')
                    infos = await page.get_by_test_id("HOUSE_CARDS_GRID_TEST_ID").get_by_role('presentation').get_by_role('heading', level=3).all_inner_texts()
                    full_address = await page.get_by_test_id("HOUSE_CARDS_GRID_TEST_ID").get_by_role('presentation').get_by_role('heading', level=2).all_inner_texts()

                    sale_prices = await page.get_by_test_id("HOUSE_CARDS_GRID_TEST_ID").get_by_role("complementary").get_by_role('paragraph').filter(has_not_text='Condo').all_text_contents()
                    ids = [locator.split('/')[4]  if len(locator.split('/')) >= 5 else '' for locator in locator_links]
                    area = [valor.split('·')[0] if len(valor.split('·')) >= 1 else '0' for valor in infos]
                    bedrooms = [valor.split('·')[1] if len(valor.split('·')) >= 2 else '0' for valor in infos]
                    garage = [valor.split('·')[2] if len(valor.split('·')) == 3 else '0' for valor in infos]
                    address = [address.split('·')[0] if len(address.split('·')) >= 1 else '' for address in full_address]
                    state = [address.split('·')[1] if len(address.split('·')) >= 2 else '' for address in full_address]
                
                    temp_data['id'] = ids
                    temp_data['total'] = sale_prices
                    temp_data['area'] = area
                    temp_data['bedroom_qtd'] = bedrooms
                    temp_data['garage'] = garage
                    temp_data['address'] = address
                    temp_data['state'] = state

                    data = pd.concat([data, temp_data], ignore_index=True).drop_duplicates()
                except ValueError as ie:
                    logging.error(f'Inconsistent extraction from {district} district')
                except Exception as ex:
                    logging.error(f'Error while storing data {ex}')
    except Exception as e:
        logging.error(f'Erro ao realizar scraping do site: {e}')
    
    finally:
        await context.close()
        await browser.close()

    return data


async def collect_districts(pw: Playwright) -> list[str]:
    districts = []

    try:
        page, response = await open_page(pw, districts_url)

        if not response.ok:
            logging.error('Requisition Error')
            
        await page.get_by_role("tab", name="Comprar", exact=True).get_by_role("paragraph").click()

        await page.get_by_role("combobox", name="Busque por cidade").click()

        await page.get_by_label("São Paulo").get_by_text("São Paulo").click()

        await page.get_by_role("combobox", name="Busque por bairro").click()

        while True:
            try:
                await page.get_by_role('combobox', name="Busque por bairro").press('ArrowDown')
                item_i = await page.get_by_role('combobox', name="Busque por bairro").get_attribute('aria-activedescendant')

                new_frame = page.locator(f'#{item_i}')
                await new_frame.wait_for(state='visible', timeout=5000)
                new_frame_text = await new_frame.text_content()

                if new_frame_text in districts:
                    break
                districts.append(new_frame_text)
            except TimeoutError:
                break
    except Exception as e:
        logging.error(f'Erro ao realizar scraping do site: {e}')
    finally:
        await page.context.close()
        await page.context.browser.close()

    return districts

async def open_page(pw: Playwright, url: str) -> list[Page | Response]:
    browser = await pw.chromium.launch(headless=False)

    context = await browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36')

    page = await context.new_page()

    response = await page.goto(url)

    return page, response


async def main():
    async with Stealth().use_async(async_playwright()) as pw:
        districts = await collect_districts(pw)
        cleaned_districts_text = [normalize_url_text(district) for district in districts]
        data = await run_spider(pw, cleaned_districts_text)
        # data = pd.DataFrame()
        # for district in districts:
        #     cleaned_district_text = normalize_url_text(district)
        #     new_data = await run_spider(pw, cleaned_district_text)
        #     if new_data.shape[0] > 0:
        #         data = pd.concat([data, new_data], ignore_index=True).drop_duplicates()
        save_data(data, output_path_name)
        

if __name__ == '__main__':  
    asyncio.run(main())