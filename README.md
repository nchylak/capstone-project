# README

This folder contains a collection of the scripts and notebooks I wrote as part of my capstone project for the Data Science Bootcamp I participated in at Propulsion Academy in Zurich.

*Note: Only part of the code written during the project is included as I excluded all the code not written by me.*

## Introduction

The goal of this project was using open data (web-scraped and public data) and Python (pandas, scikit-learn) for predicting e-commerce credit default.

We used the following sources of data: 

* web archives (14.6 Million webpages) of French (`.fr`) domains, including the web-technologies used by them
* a relational database (mySQL) including the economic and legal data of 28 million French establishments
* an XML database containing all publications made by the French public gazette, including decisions relative to solvency procedures.

We worked with the following volumes:

| **Base volume**                   | **Subset**                                                   |
| --------------------------------- | ------------------------------------------------------------ |
| 14.6 million web archives         | 14,874 e-commerce domains                                    |
| 14,874 e-commerce domains         | 3,573 SIRENs                                                 |
| 3,573 SIRENs                      | 3,063 rows (excluding foreign companies and individual entrepreneurs) |
| 3,063 rows                        | 89 bankruptcies (2,9%)                                       |
| **Financial features**            |                                                              |
| 3,063 rows                        | 868 rows with no missing values                              |
| 868 rows with no missing values   | 25 bankruptcies (2.8%)                                       |
| **Non-financial features**        |                                                              |
| 3,063 rows                        | 3,045 rows with no missing values                            |
| 3,045 rows with no missing values | 88 bankruptcies (2.9%)                                       |

## Cleaning

This part of the project essentially consisted in iterating through a database of 14.6M pages of web archives for identifying e-commerce domains (based on the technology used by the website) and their corresponding  company ID (also know as SIREN).

## Feature extraction

This part of the project consisted mainly in iterating through the domains/SIRENs identify for extracting: 

* the label (bankrupt vs. non-bankrupt)
* financial features traditional used in credit risk assessement
* non-financial features which could help assess solvency.

The following features could be extracted: 

| name                       | type        | description                                                  | shape | missing values | %missing values |
| -------------------------- | ----------- | ------------------------------------------------------------ | ----- | -------------- | --------------- |
| label                      | label       | 1 = subject to a "procédure collective"                      | 3573  | 0              | 0.00%           |
| LTdebt-to-equity           | numerical   | solvency ratio                                               | 3573  | 2350           | 65.77%          |
| current_ratio              | numerical   | liquidity ratio                                              | 3573  | 2351           | 65.80%          |
| debt-to-assets             | numerical   | solvency ratio                                               | 3573  | 2093           | 58.58%          |
| debt-to-equity             | numerical   | solvency ratio                                               | 3573  | 2093           | 58.58%          |
| debt-to-income             | numerical   | solvency ratio                                               | 3573  | 2412           | 67.51%          |
| financial_leverage         | numerical   | solvency ratio                                               | 3573  | 2091           | 58.52%          |
| profitability              | numerical   | profitability ratio                                          | 3573  | 2459           | 68.82%          |
| quick_ratio                | numerical   | liquidity ratio                                              | 3573  | 2351           | 65.80%          |
| balance_sheet_type         | categorical | C = complet, S = simplifié, K = consolidé                    | 3573  | 2043           | 57.18%          |
| nb_domains                 | numerical   | number of domains by SIREN                                   | 3573  | 0              | 0.00%           |
| employer                   | boolean     | 1 yes, 0 no                                                  | 3573  | 0              | 0.00%           |
| legal_form                 | categorical | legal form of company                                        | 3573  | 15             | 0.42%           |
| type_capital               | categorical | F = fixed capital, V = variable capital and EI = entreprise individuelle (no   capital per se) | 3573  | 22             | 0.62%           |
| ccy_capital                | categorical | ISO code of currency of capital amount                       | 3573  | 505            | 14.13%          |
| sub-region                 | categorical | département                                                  | 3573  | 23             | 0.64%           |
| region                     | categorical | région (according to new region system)                      | 3573  | 23             | 0.64%           |
| activity_class             | categorical | activity according to 'nomenclature activité'                | 3573  | 501            | 14.02%          |
| years_since_creation       | numerical   | years since creation                                         | 3573  | 28             | 0.78%           |
| amount_capital             | numerical   | maximum of 'capital' and 'capital actuel'                    | 3573  | 505            | 14.13%          |
| personality_type           | boolean     | 1=PP, 0=PM                                                   | 3573  | 0              | 0.00%           |
| https_flag                 | boolean     | 1=use https, 0=do not use https                              | 3573  | 0              | 0.00%           |
| own_email_domain           | boolean     | 1=own email domain                                           | 3573  | 0              | 0.00%           |
| trust_av_flag              | boolean     | 1=member of avis vérifés                                     | 3573  | 0              | 0.00%           |
| trust_sag_flag             | boolean     | 1=member of société des avis garantis                        | 3573  | 0              | 0.00%           |
| trust_ts_flag              | boolean     | 1=member of Trusted Shop                                     | 3573  | 0              | 0.00%           |
| trust_flag                 | boolean     | 1=member of any of the above                                 | 3573  | 0              | 0.00%           |
| translation_in_english     | boolean     | 1 = webpages in English                                      | 3573  | 0              | 0.00%           |
| nb_languages               | numerical   | number of languages found by wappalyzer                      | 3573  | 0              | 0.00%           |
| tech_ecommerce             | categorical | PrestaShop,   WooCommerce, Magento, Other                    | 3573  | 0              | 0.00%           |
| tech_cms                   | boolean     | 1 = presence of a content management system                  | 3573  | 0              | 0.00%           |
| tech_widgets               | boolean     | 1 = presence of links to social media or other sharing options | 3573  | 0              | 0.00%           |
| tech_analytics             | boolean     | 1 = presence of analytics tools                              | 3573  | 0              | 0.00%           |
| tech_enhanced_advertisment | boolean     | 1 = use made of search engine optimizers, advertising-networks, and/or   marketing-automation | 3573  | 0              | 0.00%           |
| tech_interactiveness       | boolean     | 1 = presence of blogs and/or live-chat apps                  | 3573  | 0              | 0.00%           |
| tech_enhanced_security     | boolean     | 1 = presence of captchas and/or a Content Delivery Network   | 3573  | 0              | 0.00%           |
| region_bin                 | categorical | North, South or Paris                                        | 3573  | 0              | 0.00%           |
| activity_class_bin         | categorical | Commerce de détail, de gros or other                         | 3573  | 0              | 0.00%           |
| nb_reviews                 | numerical   | Number of reviews on Trustpilot                              | 3573  | 3289           | 92.05%          |
| trust_score                | numerical   | Review score on Trustpilot (from 0 to 10)                    | 3573  | 3289           | 92.05%          |

## Modeling

This folder essentially contains a pipeline for: 

* Preparing the features
  * read a Googlesheet where the feature selection is performed (1= include)
  * split between train and test
  * scale the features and transform them into NumPy arrays
  * resample the train data due to class imbalance
* Modeling
  * for a given threshold, save the best model’s (obtained through grid search) precision, recall, ROC curve to a `.docx` file

