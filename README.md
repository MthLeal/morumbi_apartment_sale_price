# Morumbi Apartament Sale Price
![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)

System to collect data from Morumbi's apartaments and predict values based on price, number of bedrooms and garage slots.

---

## Used tech stack

- **Python: 3.13**
- **Pandas: 3.0.2**
- **Playwright: 1.59.0**

---

## Structure overview

This project combines the following steps:

1. **Data Extraction** - Scraping data from the [QuintoAndar](https://www.quintoandar.com.br/) website
2. **Data Transformation** - Cleaning and converting data extracted to be available for the model training
3. **Exploratory Data Analysis** - Creating notebooks to take insights from data
3. **Feature Engineering** - Enconding and combining features to use on the training
4. **Model Training** - Splitting data, train the model and evaluate the performance
