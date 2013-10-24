# X

X is a [business rule system](http://en.wikipedia.org/wiki/Business_rules_engine) that provides a consistent way to express business rules for use primarily in Python, Javascript, and .Net applications. Business rule systems help externalize operational decisions from application code so that application systems can more easily adapt to changing business conditions and applications can avoid having business logic mixed with functional code.

X is very heavily based on the [WebObjects DirectToWeb](https://developer.apple.com/legacy/library/documentation/WebObjects/Developing_With_D2W/) [rule system](https://developer.apple.com/legacy/library/documentation/WebObjects/Developing_With_D2W/Architecture/Architecture.html#//apple_ref/doc/uid/TP30001015-DontLinkChapterID_2-BAJDAABJ), with control semantics from Foundation and Core Data in Mac OS X and iOS, and syntax based on CSS with [LESS](http://lesscss.org/#-nested-rules) and [Saas](http://sass-lang.com/guide#3) style nesting.

## Brief History

WebObjects is an object-oriented web application framework originally released by NeXT Software in 1996. One of the features of WebObjects 4.0 was DirectToWeb (D2W), a framework that automatically generated entire web applications for database objects based on metadata provided by Enterprise Objects Framework (EOF) objects and business logic delivered by the D2W Rule Engine.

WebObjects became an Apple product when NeXT was acquired in 1997. It was largely deprecated and discontinued outside of Apple between 2006 and 2009. A variation of EOF became the Core Data framework in Mac OS X 10.4 Tiger, introducing modern versions of the underlying classes used by the D2W rule engine, but not the rule engine itself.

## Design

X is meant to operate like the D2W Rule Engine, but with Core Data's control classes replacing EOF's classes, and syntax based on CSS. D2W rules provide key-value inferences. To obtain a value for a key, rules are evaluated in a defined order until a rule with a qualifying condition is found, then it is processed (fired in D2W terminology) to produce a value.

For example, suppose a search application needed to know how many items to display per page of search results. It queries the rule engine for a key named `numberOfResultsPerPage` that returns the numer of results to show. Rules can be thought of as “if-then” statements like the following.

for `numberOfResultsPerPage`
    if today.weekday == 'Monday' then 10
    if today.weekday == 'Friday' then 20
    if true then 15

If rule system would evaluate each rule in order, and return the value for the first rule whose condition was true. If today was Monday, then it would return 10 for `numberOfResultsPerPage`. If it was Wednesday, the first two rules evaluate to false, while the last rule always evaluates to true, so it would return 15.

The `if` portion of the rule describes the conditions under which that rule is valid. It is also known as the left-hand side (lhs) of the rule.

The `then` portion is the action to take if the condition is true. In this system, it is the value to assign to the queried key. This is also known as the right-hand side (rhs) of the rule.

### Conditions (left-hand side)

The D2W Rule Engine used [EOQualifier](https://developer.apple.com/legacy/library/documentation/LegacyTechnologies/WebObjects/WebObjects_5/EOControlRef/Java/Classes/EOQualifier.html) and [Assignment](https://developer.apple.com/legacy/library/documentation/LegacyTechnologies/WebObjects/WebObjects_5/DirectToWebRef/Java/Classes/Assignment.html) classes to describe rules. X rules are based on [NSPredicate](https://developer.apple.com/library/mac/documentation/Cocoa/Reference/Foundation/Classes/NSPredicate_Class/Reference/NSPredicate.html) and [NSExpression](https://developer.apple.com/library/mac/documentation/Cocoa/Reference/Foundation/Classes/NSExpression_Class/Reference/NSExpression.html#//apple_ref/occ/cl/NSExpression) classes.

### Value (right-hand side)



### Rule Format Syntax

Predicate {
  key: Expression !priority

  (AND) Predicate {
    …
  }
}

## Web Services

## Clients

* Python
* Coffescript (Javascript)
* Objective-C
* C#
* PHP
