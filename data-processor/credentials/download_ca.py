#!/usr/bin/env python3
"""
Script to download Amazon Root CA certificate for AWS IoT
"""
import os
import urllib.request

def download_amazon_root_ca():
    """Download Amazon Root CA 1 certificate"""
    ca_url = "https://www.amazontrust.com/repository/AmazonRootCA1.pem"
    ca_filename = "AmazonRootCA1.pem"
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    ca_path = os.path.join(current_dir, ca_filename)
    
    if os.path.exists(ca_path):
        print(f"✅ {ca_filename} already exists")
        return ca_path
    
    try:
        print(f"Downloading {ca_filename} from {ca_url}")
        urllib.request.urlretrieve(ca_url, ca_path)
        print(f"✅ Downloaded {ca_filename} to {ca_path}")
        return ca_path
    except Exception as e:
        print(f"❌ Failed to download {ca_filename}: {e}")
        return None

if __name__ == "__main__":
    download_amazon_root_ca()
