import unittest
def main():
    import comment_test_browser_contract_scan
    import comment_test_browser_contract_send

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(comment_test_browser_contract_scan.TestCommentBrowserScanContractExt))
    suite.addTests(loader.loadTestsFromTestCase(comment_test_browser_contract_send.TestCommentBrowserSendContractExt))
    runner = unittest.TextTestRunner(verbosity=0)
    result = runner.run(suite)
    if not result.wasSuccessful():
        pass
if __name__ == '__main__':
    main()
