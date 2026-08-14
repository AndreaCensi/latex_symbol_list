.PHONY: clean

clean:
	coverage erase
	rm -rf $(out) $(out)/coverage $(out)/test-results
