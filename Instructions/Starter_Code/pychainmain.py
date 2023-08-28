# Modified version of the provided code

import streamlit as st
from dataclasses import dataclass
from typing import Any, List
import datetime as datetime
import pandas as pd
import hashlib

@dataclass
class Transaction:
    source: str
    destination: str
    funds: float

@dataclass
class LedgerBlock:
    transaction: Transaction
    creator_key: int
    ancestor_hash: str = "0"
    timestamp: str = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    salt: int = 0

    def compute_hash(self):
        sha = hashlib.sha512()  # Using sha512 for a different hashing mechanism

        transaction = str(self.transaction).encode()
        sha.update(transaction)

        creator_key = str(self.creator_key).encode()
        sha.update(creator_key)

        timestamp = str(self.timestamp).encode()
        sha.update(timestamp)

        ancestor_hash = str(self.ancestor_hash).encode()
        sha.update(ancestor_hash)

        salt = str(self.salt).encode()
        sha.update(salt)

        return sha.hexdigest()

@dataclass
class StreamChain:
    ledger: List[LedgerBlock]
    complexity: int = 4

    def mine_block(self, ledger_block):
        computed_hash = ledger_block.compute_hash()
        zeros_prefix = "0" * self.complexity
        while not computed_hash.startswith(zeros_prefix):
            ledger_block.salt += 1
            computed_hash = ledger_block.compute_hash()
        print("Achieved Hash", computed_hash)
        return ledger_block

    def append_block(self, candidate_block):
        ledger_block = self.mine_block(candidate_block)
        self.ledger.append(ledger_block)

    def verify_chain(self):
        block_hash = self.ledger[0].compute_hash()
        for block in self.ledger[1:]:
            if block_hash != block.ancestor_hash:
                print("Chain is compromised!")
                return False
            block_hash = block.compute_hash()
        print("Chain Integrity Confirmed")
        return True

@st.cache_resource
def initialize():
    print("Setting up StreamChain 🌐")
    return StreamChain([LedgerBlock(Transaction("Origin", "N/A", 0.0), 0)])

st.markdown("# StreamChain 🌐")
st.markdown("### Register a Transaction in the StreamChain ⛓")

streamchain = initialize()

source = st.text_input("Source ⬆️")
destination = st.text_input("Destination ⬇️")
funds = st.number_input("Funds 💰", min_value=0.0, step=0.01)

if st.button("Commit Transaction"):
    last_block = streamchain.ledger[-1]
    last_block_hash = last_block.compute_hash()
    fresh_block = LedgerBlock(
        Transaction(source, destination, funds),
        creator_key=101,
        ancestor_hash=last_block_hash
    )
    streamchain.append_block(fresh_block)
    st.balloons()

st.markdown("### The StreamChain Ledger 📘")
streamchain_df = pd.DataFrame(streamchain.ledger).astype(str)
st.write(streamchain_df)

complexity = st.sidebar.slider("Block Complexity 🔐", 1, 5, 2)
streamchain.complexity = complexity

st.sidebar.write("## Inspect Blocks 🧐")
chosen_block = st.sidebar.selectbox(
    "Pick a block to inspect 🧪", streamchain.ledger
)
st.sidebar.write(chosen_block)

if st.button("Authenticate StreamChain"):
    st.write(streamchain.verify_chain())
