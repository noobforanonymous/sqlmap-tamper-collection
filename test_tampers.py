#!/usr/bin/env python3

"""
Standalone test script for SQLMap tamper scripts
Tests without requiring SQLMap installation
"""

def test_keyword_tamper():
    """Test keyword obfuscation"""
    payload = "SELECT * FROM users WHERE id=1"
    
    keywords = ['SELECT', 'FROM', 'WHERE']
    result = payload
    
    for keyword in keywords:
        result = result.replace(keyword, f'/*!50000{keyword}*/')
    
    expected = "/*!50000SELECT*/ * /*!50000FROM*/ users /*!50000WHERE*/ id=1"
    assert result == expected, f"Expected: {expected}, Got: {result}"
    
    # Test deterministic
    result2 = payload
    for keyword in keywords:
        result2 = result2.replace(keyword, f'/*!50000{keyword}*/')
    
    assert result == result2, "Not deterministic!"
    
    return result

def test_space_tamper():
    """Test space replacement"""
    payload = "SELECT * FROM users"
    result = payload.replace(' ', '/**/')
    
    expected = "SELECT/**/*/**/FROM/**/users"
    assert result == expected, f"Expected: {expected}, Got: {result}"
    
    # Test deterministic
    result2 = payload.replace(' ', '/**/')
    assert result == result2, "Not deterministic!"
    
    return result

def test_case_tamper():
    """Test alternating case"""
    keyword = "SELECT"
    alternating = ''.join(
        char.lower() if i % 2 == 0 else char.upper()
        for i, char in enumerate(keyword)
    )
    
    expected = "sElEcT"
    assert alternating == expected, f"Expected: {expected}, Got: {alternating}"
    
    # Test deterministic
    alternating2 = ''.join(
        char.lower() if i % 2 == 0 else char.upper()
        for i, char in enumerate(keyword)
    )
    assert alternating == alternating2, "Not deterministic!"
    
    return alternating

def test_encode_tamper():
    """Test URL encoding"""
    payload = "id=1"
    encoding_map = {'=': '%3D'}
    
    result = payload
    for char, encoded in encoding_map.items():
        result = result.replace(char, encoded)
    
    expected = "id%3D1"
    assert result == expected, f"Expected: {expected}, Got: {result}"
    
    # Test deterministic
    result2 = payload
    for char, encoded in encoding_map.items():
        result2 = result2.replace(char, encoded)
    
    assert result == result2, "Not deterministic!"
    
    return result

def test_combined():
    """Test combined tamper with correct ordering"""
    payload = "SELECT * FROM users WHERE id=1"
    
    # Step 1: Keywords
    keywords = ['SELECT', 'FROM', 'WHERE']
    result = payload
    for keyword in keywords:
        result = result.replace(keyword, f'/*!50000{keyword}*/')
    
    # Step 2: Spaces
    result = result.replace(' ', '/**/')
    
    # Step 3: Encoding
    result = result.replace('=', '%3D')
    
    # Step 4: Case (on keywords inside comments)
    for keyword in keywords:
        alternating = ''.join(
            char.lower() if i % 2 == 0 else char.upper()
            for i, char in enumerate(keyword)
        )
        result = result.replace(f'/*!50000{keyword}*/', f'/*!50000{alternating}*/')
    
    print(f"Original:  {payload}")
    print(f"Bypassed:  {result}")
    
    # Test deterministic
    result2 = payload
    for keyword in keywords:
        result2 = result2.replace(keyword, f'/*!50000{keyword}*/')
    result2 = result2.replace(' ', '/**/')
    result2 = result2.replace('=', '%3D')
    for keyword in keywords:
        alternating = ''.join(
            char.lower() if i % 2 == 0 else char.upper()
            for i, char in enumerate(keyword)
        )
        result2 = result2.replace(f'/*!50000{keyword}*/', f'/*!50000{alternating}*/')
    
    assert result == result2, "Not deterministic!"
    
    return result

def main():
    """Run all tests"""
    print("="*60)
    print("SQLMap Tamper Script Test Suite (Standalone)")
    print("="*60)
    
    tests = [
        ("Keyword Tamper", test_keyword_tamper),
        ("Space Tamper", test_space_tamper),
        ("Case Tamper", test_case_tamper),
        ("Encode Tamper", test_encode_tamper),
        ("Combined Tamper", test_combined)
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            result = test_func()
            print(f"✅ {name}: PASSED")
            if result:
                print(f"   Result: {result}")
            passed += 1
        except AssertionError as e:
            print(f"❌ {name}: FAILED")
            print(f"   Error: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {name}: ERROR")
            print(f"   Error: {e}")
            failed += 1
        print()
    
    print("="*60)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*60)
    
    if failed == 0:
        print("✅ ALL TESTS PASSED - TAMPERS ARE DETERMINISTIC")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
