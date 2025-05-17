import os, json
from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
from web3 import Web3
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(dotenv_path=env_path, override=True)

contract_address = os.getenv("CONTRACT_ADDRESS")
if not contract_address:
    raise Exception("CONTRACT_ADDRESS não encontrado no arquivo .env")

print(f"Usando CONTRACT_ADDRESS: {contract_address}")

w3 = Web3(Web3.HTTPProvider(os.getenv("POLYGON_RPC")))

with open("hardhat/artifacts/contracts/Voting.sol/SimpleVoting.json") as f:
    abi = json.load(f)["abi"]

contract = w3.eth.contract(
    address=Web3.to_checksum_address(os.getenv("CONTRACT_ADDRESS")),
    abi=abi
)

ACCOUNT = Web3.to_checksum_address(os.getenv("PUBLIC_ADDRESS"))
PK      = os.getenv("PRIVATE_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")


def verify_api_key(x_api_key: str = Header(None)):
    if SECRET_KEY and x_api_key == SECRET_KEY:
        return True
    raise HTTPException(status_code=401, detail="Invalid or missing API key")


class VoteIn(BaseModel):
    pollId: int
    option: str


app = FastAPI(title="Micro-Voting (Polygon)")

@app.post("/vote", dependencies=[Depends(verify_api_key)])
def vote(data: VoteIn):
    try:
        nonce = w3.eth.get_transaction_count(ACCOUNT)
        txn = contract.functions.vote(data.pollId, data.option).build_transaction({
            "nonce": nonce,
            "maxPriorityFeePerGas": w3.to_wei("25", "gwei"),
            "maxFeePerGas":        w3.to_wei("50", "gwei"),
            "gas":  80_000,
        })
        signed = w3.eth.account.sign_transaction(txn, private_key=PK)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        
        w3.eth.wait_for_transaction_receipt(tx_hash)
        
        return {"tx_hash": w3.to_hex(tx_hash)}
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/results/{poll_id}", dependencies=[Depends(verify_api_key)])
def results(poll_id: int):
    try:
        logs = contract.events.Voted.get_logs(
            from_block=0,
            to_block="latest",
            argument_filters={"pollId": poll_id}
        )

        counts = {}
        for log in logs:
            opt = log["args"]["option"]
            counts[opt] = counts.get(opt, 0) + 1

        return {
            "pollId": poll_id,
            "totais": counts,
            "totalVotos": sum(counts.values()),
            "txCount": len(logs)
        }
    except Exception as e:
        raise HTTPException(500, str(e))