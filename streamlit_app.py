import streamlit as st
import pandas as pd
import numpy as np
import random
import json
import logging
import time
from itertools import islice


logging.basicConfig(level=logging.INFO)


# Streamlit state to store data
@st.cache(allow_output_mutation=True)
def get_state():
    return {}

state = get_state()

# Function to generate and save merchant-pincodes relationships
def generate_and_save_data():
    logging.info("Start generating data ...")
    # Set the scale for the demonstration
    num_merchants = 10000000
    num_pincodes = 30000

    # Generate merchant IDs and pincodes
    merchants = [f"Merchant_{i+1}" for i in range(num_merchants)]
    unique_pincodes = set()
    while len(unique_pincodes) < num_pincodes:
        unique_pincodes.add(str(random.randint(100000, 999999)))
    pincodes = list(unique_pincodes)

    # Randomly assign some pincodes to each merchant to simulate the sparse nature
    relationship_dict = {}
    for merchant in merchants:
        num_served_pincodes = random.randint(1, 5)
        served_pincodes = random.sample(pincodes, num_served_pincodes)
        relationship_dict[merchant] = served_pincodes

    # Save to a JSON file
    with open('merchants/merchant.json', 'w') as f:
        json.dump(relationship_dict, f)

    # Update Streamlit state
    state['relationship_dict'] = relationship_dict
    logging.info("Done generating data ...")

# Function to create an inverted index
def create_inverted_index():
    logging.info("Start creating inverted_index data ...")
    inverted_index = {}

    if 'relationship_dict' in state:
        relationship_dict = state['relationship_dict']

        for merchant, pincodes in relationship_dict.items():
            for pincode in pincodes:
                if pincode not in inverted_index:
                    inverted_index[pincode] = []
                inverted_index[pincode].append(merchant)

        # Save inverted index to a JSON file
        with open('merchants/inverted_index.json', 'w') as f:
            json.dump(inverted_index, f)

        # Update Streamlit state
        state['inverted_index'] = inverted_index

        st.success("Inverted index created and saved successfully!")
        logging.info("Done creating inverted_index data ...")

# Function to search pincode serviceability
def search_pincode(pincode):
    logging.info("Start search data ...")
    if 'inverted_index' in state:
        if pincode in state['inverted_index']:
            st.success(f"Pincode {pincode} is servicable.")
            st.subheader("Merchants serving this pincode:")
            merchants_list = state['inverted_index'][pincode]
            for merchant in merchants_list:
                st.markdown(f"- {merchant}")
        else:
            st.warning(f"Pincode {pincode} is not servicable.")
        logging.info("Found search data ...")
    logging.info("NotFound search data ...")

  
# Function to insert new merchant-pincode pair
def insert_merchant_pincode(merchant, pincode):
    logging.info("Start Insert data ...")
    if 'relationship_dict' in state:
        relationship_dict = state['relationship_dict']

        # Update state
        if merchant in relationship_dict:
            relationship_dict[merchant].append(pincode)
        else:
            relationship_dict[merchant] = [pincode]

        # Save relationship_dict to a JSON file
        with open(f'merchants/merchant.json', 'w') as f:
            json.dump(relationship_dict, f)

        # Update inverted index
        if 'inverted_index' in state:
            inverted_index = state['inverted_index']
            if pincode in inverted_index:
                inverted_index[pincode].append(merchant)
            else:
                inverted_index[pincode] = [merchant]

            # Save inverted index to a JSON file
            with open('merchants/inverted_index.json', 'w') as f:
                json.dump(inverted_index, f)

        st.success(f"Merchant-Pincode pair ({merchant}, {pincode}) added successfully!")
        logging.info("Done Insert data ...")

# ... (rest of the script remains unchanged)

# Function to validate merchant format
def validate_merchant_format(merchant):
    return merchant.startswith("Merchant_") and merchant[9:].isdigit()

# Function to validate pincode format
def validate_pincode_format(pincode):
    return pincode.isdigit() and len(pincode) == 6

# Streamlit UI
st.title("Merchant-Pincodes Relationship and Search")

# Create tabs
tabs = st.tabs(["Relationships", "Search", "Insert"])

# First tab: Relationships
with tabs[0]:
    # Button to generate and save data

    if "data_generated" not in state or state['data_generated'] == False :
        st.info("Generating sample Sparse matrix for 10 Million Merchants and 30 Thousand pincodes.")
        generate_and_save_data()
        st.info("Data representation done using hash map and inverted index for efficient search and insert operations.")
        create_inverted_index()
        st.success("Data generated and saved successfully!")
        state['data_generated'] = True

    # Display the generated data in a scrollable window with each key-value pair on a new line
    if 'relationship_dict' in state:
        # data_display = st.empty()
        sample_size = min(10, len(state['relationship_dict']))
        # data_content = "\n".join([f"{key}: {value}" for key, value in list(state['relationship_dict'].items())[:sample_size]])
        # data_display.text_area('', data_content, height=300, max_chars=0)

        # Display a small sample of the 2D sparse matrix
        st.header("Sample of 2D Sparse Matrix:")
        matrix_display = st.empty()
        merchants = list(state['relationship_dict'].keys())[:sample_size]
        pincodes = list()
        for merchant in merchants:
            pincodes += list(state['relationship_dict'][merchant])
        pincodes = pincodes[:min(len(pincodes),50)]

        # Create a 2D NumPy array representing the sparse matrix
        sparse_matrix = np.zeros((len(merchants), len(pincodes)))
        for i, merchant in enumerate(merchants):
            for j, pincode in enumerate(pincodes):
                if pincode in state['relationship_dict'][merchant]:
                    sparse_matrix[i, j] = 1

        # Display the matrix using a DataFrame
        matrix_df = pd.DataFrame(sparse_matrix, index=merchants, columns=pincodes)
        matrix_display.dataframe(matrix_df)

        # st.header("Generated Hash map !!")
        st.header("Representation for servicable Pinciodes of Merchants")
        data_display = st.empty()
        data_content = "\n".join([f"{key}: {value}" for key, value in islice(state['relationship_dict'].items(), 10)])
        data_display.text_area('', data_content, height=300, max_chars=0)
    
    # Button to create inverted index (conditionally displayed)
    # if 'data_generated' in state and state['data_generated']:
    #     if st.button("Generate Inverted Index"):
            

    # # Display the inverted index in a scrollable window with each key-value pair on a new line
    # if 'inverted_index' in state:
    #     st.header("Generated Inverted Index !!")
        st.header("Representation for Merchants servicing at a particular Pinciode")
        inverted_index_display = st.empty()
        inverted_index_content = "\n\n".join([f"{key}: {value}" for key, value in islice(state['inverted_index'].items(),5)])
        inverted_index_display.text_area('', inverted_index_content, height=300, max_chars=0)

# Second tab: Search
with tabs[1]:
    st.header("Search Pincode Serviceability")
    pincode_input = st.text_input("Enter Pincode to search:")
    if st.button("Search"):
        if pincode_input:
            search_pincode(pincode_input)
        else:
            st.warning("Please enter a Pincode.")

# Third tab: Insert
with tabs[2]:
    st.header("Insert Merchant-Pincode Pair")
    merchant_input = st.text_input("Enter Merchant:")
    pincode_input_insert = st.text_input("Enter servicable Pincode:")
    if st.button("Insert"):
        if validate_merchant_format(merchant=merchant_input) is False or validate_pincode_format(pincode=pincode_input_insert)is False:
            st.warning("Please enter correct MerchantId and Pincode.")
        else:
            if merchant_input and pincode_input_insert:
                insert_merchant_pincode(merchant_input, pincode_input_insert)
            else:
                st.warning("Please enter both Merchant and Pincode.")
