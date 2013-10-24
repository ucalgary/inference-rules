# X

X is a [business rule system](http://en.wikipedia.org/wiki/Business_rules_engine) that provides a consistent way to express business rules for use primarily in Python, Javascript, and .Net applications. Business rule systems help externalize operational decisions from application code so that application systems can more easily adapt to changing business conditions and applications can avoid having business logic mixed with functional code.

X is very heavily based on the [WebObjects DirectToWeb](https://developer.apple.com/legacy/library/documentation/WebObjects/Developing_With_D2W/) [rule system](https://developer.apple.com/legacy/library/documentation/WebObjects/Developing_With_D2W/Architecture/Architecture.html#//apple_ref/doc/uid/TP30001015-DontLinkChapterID_2-BAJDAABJ), with control semantics from Foundation and Core Data in Mac OS X and iOS, and syntax based on CSS with [LESS](http://lesscss.org/#-nested-rules) and [Saas](http://sass-lang.com/guide#3) style nesting.

## Brief History

WebObjects is an object-oriented web application framework originally released by NeXT Software in 1996. One of the features of WebObjects 4.0 was DirectToWeb (D2W), a framework that automatically generated entire web applications for database objects based on metadata provided by [Enterprise Objects Framework](http://en.wikipedia.org/wiki/Enterprise_Objects_Framework) (EOF) objects and business logic delivered by the D2W Rule Engine.

WebObjects became an Apple product when NeXT was acquired in 1997. It was largely deprecated and discontinued outside of Apple between 2006 and 2009. Many concepts from EOF appeared in Core Data— introduced in Mac OS X 10.4 Tiger (and later in iOS 3)—bringing modern versions of the underlying control classes used by the D2W rule engine, but not the rule engine itself.

## Design

X is meant to operate like the D2W Rule Engine, but with Core Data control classes replacing EOF classes, and syntax based on CSS. D2W rules provide key-value inferences. Simple key-value objects—such as a dictionary—contain pairs of keys and values that can be retrieved by keys. For example, the following dictionary contains information related to configuring a search results page.

```
{
  'numberOfResultsPerPage': 20,
  'nextPageIconName': 'next.png',
  'pageTitleFormat': 'Search Results Page %i of %i'
}
```

A web application can determine how many results to show per page by querying the dictionary for the `numberOfResultsPagePage` key. Each key-value pair in this dictionary contains simple bits of business logic that can feed into an application.

A rule engine with key-value inferences expands on this idea by allowing each key to have more than one possible value, where each value contains criteria of when it applies. Suppose the `numberResultsPerPage` could vary depending on the type of user that was viewing the page.

```
for `numberOfResultsPerPage`
  if user.type == 'Power User' then 40
  if user.type == 'Novice' then 10
  if true then 20
```

To determine the value of `numberOfResultsPerPage`, the rule engine would evaluate the listed rules in order until the first one that matches the current conditions. For a power user, it would return 40; for a novice, 10. For all other users (the rule that always evaluates to true), it would return 20.

The `if` portion of the rule describes the conditions under which that rule is valid. This is known as the left-hand side (lhs) of the rule.

The `then` portion is the action to take if the condition is true. In a key-value inference system, it is the value to assign to the queried key. This is known as the right-hand side (rhs) of the rule.

### Conditions (left-hand side)

The D2W Rule Engine used [EOQualifier](https://developer.apple.com/legacy/library/documentation/LegacyTechnologies/WebObjects/WebObjects_5/EOControlRef/Java/Classes/EOQualifier.html) and [Assignment](https://developer.apple.com/legacy/library/documentation/LegacyTechnologies/WebObjects/WebObjects_5/DirectToWebRef/Java/Classes/Assignment.html) classes to describe rules. X rules are based on [NSPredicate](https://developer.apple.com/library/mac/documentation/Cocoa/Reference/Foundation/Classes/NSPredicate_Class/Reference/NSPredicate.html) and [NSExpression](https://developer.apple.com/library/mac/documentation/Cocoa/Reference/Foundation/Classes/NSExpression_Class/Reference/NSExpression.html#//apple_ref/occ/cl/NSExpression) classes.

### Values (right-hand side)



## Rule Format Syntax

Predicate {
  key: Expression !priority

  (AND) Predicate {
    …
  }
}

## Differences from Direct To Web

## Web Services

## Clients

* Python
* Coffescript (Javascript)
* Objective-C
* C#
* PHP
