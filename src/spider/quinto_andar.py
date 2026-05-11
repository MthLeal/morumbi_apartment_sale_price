import asyncio
import pandas as pd
from playwright.async_api import async_playwright, Playwright, TimeoutError

async def run(pw: Playwright) -> pd.DataFrame:
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

        # abrir o navegador
        page = await context.new_page()

        # abre a pagina
        await page.goto('https://www.quintoandar.com.br/comprar/imovel/morumbi-sao-paulo-sp-brasil/de-150000-a-200000-venda')
        
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
                print('Nao existe mais botao carregar mais')
                break
        
        locator_links = await page.get_by_test_id("HOUSE_CARDS_GRID_TEST_ID").get_by_test_id('house-card-container').get_by_role('link').all()
        link_ids = [await locator.get_attribute('href') for locator in locator_links]
        infos = await page.get_by_test_id("HOUSE_CARDS_GRID_TEST_ID").get_by_role('presentation').get_by_role('heading', level=3).all_inner_texts()
        full_address = await page.get_by_test_id("HOUSE_CARDS_GRID_TEST_ID").get_by_role('presentation').get_by_role('heading', level=2).all_inner_texts()

        ids = [link_id.split('/')[2] for link_id in link_ids]
        sale_prices = await page.get_by_test_id("HOUSE_CARDS_GRID_TEST_ID").get_by_role("complementary").get_by_role('paragraph').filter(has_not_text='Condo').all_text_contents()
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
        print(f'Erro ao realizar scraping do site: {e}')
    
    finally:
        await context.close()
        await browser.close()

    return data

def save_data(data:pd.DataFrame):
    data.to_parquet('./data/house_data.parquet', index=False)

async def main():
    async with async_playwright() as pw:
        data = await run(pw)
        save_data(data)

asyncio.run(main())