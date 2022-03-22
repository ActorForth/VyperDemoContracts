.PHONY: help

add-network:
		brownie networks add Ethereum SmartBCH_testnet2 host=http://35.220.203.194:8545/ chainid=10001

install-dependencies:
		pip install -r requirements.txt	

init: install-dependencies add-network


test:
		brownie test --coverage -v 

test-bdd:
	# show report
		brownie test -s --feature features --gherkin-terminal-reporter

deploy-local:
		brownie run deploy.py --network development

deploy-regtest:
		brownie run deploy.py --network regtest_scorpion02

performance-test:
	brownie test tests/test_Blockchain_Performance.py --network avax-test --durations=0 --gas

