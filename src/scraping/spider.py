import asyncio
from playwright.async_api import async_playwright, Playwright, TimeoutError

async def run(pw: Playwright):
    browser = await pw.chromium.launch(headless=False)

    context = await browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36')

    # abrir o navegador
    page = await context.new_page()

    # stealth = Stealth()
    # stealth.apply_stealth_sync(page)

    # abre a pagina
    await page.goto('https://www.quintoandar.com.br/')

    # localiza na pagina
    botao_comprar_casa = page.get_by_role("tab", name="Comprar", exact=True).get_by_role("paragraph")
    await botao_comprar_casa.wait_for(state='visible')
    await botao_comprar_casa.click()

    # preencher cidade sao paulo
    await page.get_by_role("combobox", name="Busque por cidade").click()
    await page.get_by_label("São Paulo").get_by_text("São Paulo").click()

    # preencher bairro
    await page.get_by_role("combobox", name="Busque por bairro").click()
    await page.get_by_role("combobox", name="Busque por bairro").fill("Morumb")
    await page.get_by_role("combobox", name="Busque por bairro").press('i')
    await page.get_by_text("Morumbi", exact=True).click()
    
    #buscar
    await page.get_by_role("button", name="Buscar imóveis").click()

    # pular personalização
    botao_pular = page.get_by_role("button", name="Pular tudo")
    await botao_pular.wait_for(state='visible')
    await botao_pular.click()

    # filtrar por apartamentos
    botao_filtro_apartamento = page.get_by_role("button", name="Tipos de imóvel, filtrar")
    await botao_filtro_apartamento.wait_for()
    await botao_filtro_apartamento.click()
    await page.get_by_role("checkbox", name="Apartamento").check()
    await page.get_by_role("button", name="Atualizar resultados").click()

    
    count_clicks = 0

    while count_clicks < 100:
        botao_carregar_mais = page.get_by_test_id("load-more-button")

        try:
            await botao_carregar_mais.wait_for(
                state='visible',
                timeout=10000
            )
            await botao_carregar_mais.click()
            count_clicks += 1

        except TimeoutError:
            print('Nao existe mais botao carregar mais')
            break

    valores = await page.get_by_role("complementary").get_by_role('paragraph').filter(has_not_text='Condo').all_text_contents()
    infos = await page.get_by_role('presentation').get_by_role('heading', level=3).all_inner_texts()
    enderecos = await page.get_by_role('presentation').get_by_role('heading', level=2).all_inner_texts()
    print(len(valores))

    for i in range(len(valores)):
        print(f'valor: {valores[i]}, infos: {infos[i]}, endereco: {enderecos[i]}')


    await context.close()
    await browser.close()


async def main():
    async with async_playwright() as pw:
        await run(pw)

asyncio.run(main())