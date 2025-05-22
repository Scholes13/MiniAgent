"""
Twitter configuration settings
"""
import os
from pathlib import Path

# Twitter credentials
TWITTER_USERNAME = "svkull13"
TWITTER_PASSWORD = "bhayangkara1"
TWITTER_EMAIL = ""  # Kosong jika menggunakan nama pengguna (username)

# Path untuk menyimpan cookies (untuk login)
BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COOKIES_FILE = os.path.join(BASE_DIR, "data", "cache", "twitter_cookies.json")

# Queries untuk pencarian airdrop
AIRDROP_SEARCH_QUERIES = [
    "crypto airdrop",
    "free airdrop token",
    "new crypto airdrop",
    "$ETH airdrop",
    "$SOL airdrop",
    "NFT airdrop",
    "airdrop giveaway",
    "claim free tokens"
]

# Hashtags crypto untuk filter trending
CRYPTO_HASHTAGS = [
    "crypto",
    "bitcoin",
    "btc",
    "eth",
    "ethereum",
    "sol",
    "solana",
    "nft",
    "defi",
    "web3",
    "blockchain",
    "airdrop",
    "altcoin",
    "binance",
    "token",
    "metaverse"
]

# Trending projects search queries
TRENDING_SEARCH_QUERIES = [
    "new crypto token",
    "crypto gem",
    "new token launch",
    "crypto presale",
    "new blockchain project"
]

# Optional Settings
LANGUAGE = "en-US"  # Bahasa default untuk Twitter client 