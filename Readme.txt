Question 5:
Performance:
The algorithm achieved a precision, recall and F1 Score of 0.714 each. It took 35.19 seconds to run on the test set.

Observations:
The three lowest F1 Scores were received by SBAR, ADVP and NP+NUM while the three highest F1 Scores were received by ., CONJ and DET.

Question 6:
Performance:
The algorithm achieved a precision, recall and F1 Score of 0.742 each. The improved performance compared to Question 5 was expected since Vertical Markovization makes use of the contextual information of a node's parent also while generating the parse tree. It took 51.73 seconds to run on the test set. The time taken was longer than Question 5 since we have more non-terminals and number of rules in the grammar.

The following sentence taken from the test set was parsed incorrectly by the parser in Question 5 but the entire parse tree was parsed correctly by the parser in Question 6:
This time , the firms were ready .
The above sentence is an example where the parser's performance improved.

Observations:
The three lowest F1 Scores were received by ADVP, NP+NUM and VP+VERB while the three highest F1 Scores were received by ., CONJ and DET.

The precision, recall and F1 Score all increased by 0.028 compared to the parser in Question 5. Except for PRT, ADJ, ADVP+ADV, NP+ADJ and PRT+PRT, the F1 Score of the parser either matched or improved upon the parser in Question 5 for all the remaining 24 non-terminals. The highest improvement in the F1 Score was seen for SBAR, which increased by 0.444 from 0.056 to 0.5. In contrast, the highest decrease in F1 Score was seen for PRT+PRT, which decreased by 0.127 from 0.571 to 0.444.

