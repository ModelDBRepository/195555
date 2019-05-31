#!/usr/bin/python2.7

import json
import re
import sys
from re import search

with open('manual_classifier_rules.json') as f:
    rules = json.load(f)

token = re.compile('[a-zA-Z0-9]+')

def tokenize(text):
    """not doing stop word removal"""
    return [word for word in token.findall(text)]

def get_n_grams_with_spaces(tokens, n):
    """return the n-grams comprised of consecutive tokens"""
    return [' %s ' % ' '.join(tokens[i : n + i]) for i in xrange(len(tokens) - n + 1)]

def an_item_matches(items, original_pattern):
    patterns = [('(?i) (%s) ' if pattern.islower() else ' (%s) ') % pattern for pattern in original_pattern.split('$')]
    for item in items:
        for pattern in patterns:
            if not search(pattern, item):
                break
        else:
            return True
    return False

def analyze_abstract(text, check_new_match=True, check_fulltext_first=True):
    """takes a text, returns a list of predicted ModelDB terms"""
    dont_check_new_match = not check_new_match
    dont_check_fulltext_first = not check_fulltext_first
    tokens = tokenize(text)
    processed_text = [' %s ' % ' '.join(tokens)]
    n_grams = get_n_grams_with_spaces(tokens, 5)
    result = set([])
    for pattern, rule in rules.iteritems():
        # only test a rule if it would give something new
        result_if_matched = result.union(rule)
        if dont_check_new_match or len(result_if_matched) > len(result):
            # check the full text first before running on all n-grams
            if dont_check_fulltext_first:
                if an_item_matches(n_grams, pattern):
                    result = result_if_matched
            elif an_item_matches(processed_text, pattern):
                if '$' not in pattern or an_item_matches(n_grams, pattern):
                    result = result_if_matched
    return result

#
# the main program
#
if __name__ == '__main__':
    try:
        with open(sys.argv[1]) as f:
            text = f.read()
    except:
        print 'Usage:'
        print '    python %s ABSTRACT_FILENAME [check_fulltext_first check_new_match]' % sys.argv[0]
        sys.exit(-1)

    if len(sys.argv) == 4:
        check_fulltext_first = sys.argv[2].lower()[0] == 't'
        check_new_match = sys.argv[3].lower()[0] == 't'
    else:
        check_fulltext_first = check_new_match = True
    result = analyze_abstract(text, check_new_match=check_new_match, check_fulltext_first=check_fulltext_first)
    print json.dumps(sorted(result), indent=4)
    print len(result), 'items'