import asyncio
import logging
import pandas as pd
from pathlib import Path
from utils.utils import save_data
from playwright.async_api import async_playwright, Playwright, TimeoutError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

output_path_name = Path(__file__).parent.parent.parent / 'data' / 'house_data2.parquet'
url = 'https://www.quintoandar.com.br/comprar/imovel/morumbi-sao-paulo-sp-brasil/apartamento'

async def run_spider(pw: Playwright) -> pd.DataFrame:
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
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36')

        # abre o navegador e a pagina
        page = await context.new_page(url)

        response = await page.goto()

        if not response.ok:
            logging.error('Requisition Error')
            return data
        
        count_clicks = 0

        while count_clicks < 100:
            botao_carregar_mais = page.get_by_test_id("load-more-button")

            try:
                await botao_carregar_mais.wait_for(
                    state='visible',
                    timeout=5000
                )
                await botao_carregar_mais.click()
                count_clicks += 1

            except TimeoutError:
                break
        
        locator_links = await page.get_by_test_id("HOUSE_CARDS_GRID_TEST_ID").get_by_test_id('house-card-container').get_by_role('link').evaluate_all('els => els.map(el => el.href)')
        infos = await page.get_by_test_id("HOUSE_CARDS_GRID_TEST_ID").get_by_role('presentation').get_by_role('heading', level=3).all_inner_texts()
        full_address = await page.get_by_test_id("HOUSE_CARDS_GRID_TEST_ID").get_by_role('presentation').get_by_role('heading', level=2).all_inner_texts()

        sale_prices = await page.get_by_test_id("HOUSE_CARDS_GRID_TEST_ID").get_by_role("complementary").get_by_role('paragraph').filter(has_not_text='Condo').all_text_contents()
        ids = [locator.split('/')[4] for locator in locator_links]
        area = [valor.split('·')[0] for valor in infos]
        bedrooms = [valor.split('·')[1] for valor in infos]
        garage = [valor.split('·')[2] if len(valor.split('·')) == 3 else '0' for valor in infos]
        address = [address.split('·')[0] for address in full_address]
        state = [address.split('·')[1] for address in full_address]

        data['id'] = ids
        data['total'] = sale_prices
        data['area'] = area
        data['bedroom_qtd'] = bedrooms
        data['garage'] = garage
        data['address'] = address
        data['state'] = state

    except Exception as e:
        logging.error(f'Erro ao realizar scraping do site: {e}')
    
    finally:
        await context.close()
        await browser.close()

    return data


async def main():
    async with async_playwright() as pw:
        data = await run_spider(pw)
        save_data(data, output_path_name)

if __name__ == '__main__':  
    asyncio.run(main())