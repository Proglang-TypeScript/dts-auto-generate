# dts-auto-generate

## Goal

We want to generate TypeScript declaration files for JavaScript libraries **without** relying on code examples or tests provided by the library's authors.

Using such code examples is problematic because they are:

* Non-exhaustive. The library might contain additional exported functions that are not shown in the code examples. The functions that are shown in the examples may also have behaviours that are not properly explained in the code. (I imagine that) functions with many configuration options suffer a lot from this.
* Stale. Code examples are not a part of the shipped library. Instead they serve as documentation. (From studies we know that) documentation material is susceptible to becoming stale, just as well as manually written TS declaration files (see e.g. TSEvolve).

## Possible approaches

### Static analysis of the JavaScript library

Pros:

* Does not require code examples by design.

Cons:

* Requires development of a custom, lightweight static analysis. Current "general" static analysis tools for JS do not scale well (I think). It might also be hard to get a sufficient degree of precision.
* A separate static analysis tool requires continual maintenance to stay abreast with JavaScript extensions.

See e.g.: [TSInfer](https://cs.au.dk/~amoeller/papers/tstools/), which is a continuation of TSCheck.
I think we will have a hard time with implementing a *better* static analysis than what they use in TSInfer. Maybe we could improve upon their work, but in that case I think it would be hard to argue for novelty.
We should evaluate our results against TSInfer's to show that we can infer more precise results than with static analysis!
PT We should also compare with respect to space and time complexity.

### Machine learning

We can use the JavaScript library code as data and the corresponding TS declaration files as targets. Maybe there are enough pairs to enable some kind of machine learning approach.

Pros: Will figure out type inference heuristics automatically.

Cons: I have little experience with machine learning algorithms and their applications. The toughest problem will probably be to encode JavaScript code into a suitable format.

TODO: Look for related work exploring this direction.

[NL2Type: Inferring JavaScript Function Types from Natural Language Information](https://ieeexplore.ieee.org/document/8811893) uses parameter names, function names and documentation (comments) to infer types.

PT here is a thought:

* the problem is to translate the type inference problem into a setting usable for machine learning; i.e. we need to translate the problem into a vector of numbers and we need training data to establish ground truth
* now: take a module which comes with a declaration file on Definitely Typed (DT), generate some sample inputs based on the declared types (IIRC this functionality is essentially provided by TSCheck)
* new element: trace the interactions of input value with type T and record which operations are applied to that value.
* this results for each x:T in a **vector** with one entry for each operation (which operations are most telling is TBD; accessing object properties might have to be handled separately, things could be normalized by mapping property names to some standard names)
* doing this for many DT modules results in many such vectors for each type T --> this is our training data
* based on this select and train the proper neural net
* for a new module, we obtain the set of interactions on each input and ask the net for the likely types!


### Combined "symbolic execution" and dynamic analysis

We can build on the original dynamic analysis idea of *dts-generate*. We will add some way to automatically generate interesting test cases or otherwise explore the library code with good coverage. Based on the dynamically observed *interactions* we can infer types.

Pros: We can reuse a lot of infrastructure from the *dts-generate* project. We do not have to implement a JavaScript (abstract) interpreter.

Cons: The quality of the output will rely a lot on how well we can exercise the library code.

We do not want to do standard symbolic execution, as this would require us to implement a JavaScript interpreter.

The current *dts-generate* approach does (to my understanding / PJT: correct) use the runtime types of argument values for type inference in a lot of cases. We do not have access to such values in our case, so type inference should be based solely on usage (patterns).
*dts-generate* also assumes that the code examples represent valid uses of the library. We will likely end up exploring code paths that correspond to error handling (due to e.g. wrong argument types) or otherwise unintended usage of the functions.

In Jalangi2 there is an option to override the result of conditions. This gives an easy way to recursively explore all possible branches in the code. Aside from the path explosion problem, you also encounter the issue that you are exploring branching pairs that are impossible in practice. Maybe an SMT solver could be used to figure out when branch combinations are invalid, but due to JavaScript's dynamic nature, I think this would be extremely difficult.
Perhaps the impact of exploring invalid branch combinations is not that high for type inference.
(PJT: I agree. The issue is that you have to take into account all the implicit conversions before you obtain clean formulas for an SMT solver.)

[TSTest](https://cs.au.dk/~amoeller/papers/tstest/) is a relevant tool/paper on how to generate tests for JavaScript libraries based on TypeScript declaration files. The tool essentially generates function arguments based on the declared types, runs the functions, and then checks whether the return value matches the type specified in the declaration file.

[Python probabilistic type inference with natural language support](https://dl.acm.org/doi/abs/10.1145/2950290.2950343) combines a machine learning algorithm for learning types based on variable names with "probabilistic inference" based on data-flow, attribute accesses and explicit type checks.
The presentation is mathematically detailed.
We should be careful that our work does not end up as a worse version of this.
(PJT: I was not aware of this paper. Would you want to discuss it in a Friday seminar?)

There are two different and slightly separate concerns that need to be implemented:

1. We must be able to infer types for arguments based on how they are used - most likely guided by heuristics such as the one from Fernando's Master thesis.

2. We must generate code examples that exercise the library in such a way that we obtain a high degree of code coverage.

#### Type inference heuristics based on variable usage

Ideas:

* Comparing the result of `typeof x` with something gives a strong hint wrt. primitive types.
* The same idea can be used to infer class types with `instanceof` .
* Field accesses and method calls indicate (an) object type.
  Possibly also Array/String/Number.
* Fernando's Master thesis gives heuristics about types of values involved in binary operators. `+` is used for both strings and numbers, others are mostly used with numbers (with the exception of equality checking operators).
* PJT: See the above ML-based idea to obtain more ideas about types from interactions.
* PJT: possibly, sequences of operations and compound operations on a value give more insight about its intended type. Examples
  * (compound) `x+1` -> x:num with high likelyhood, althogh x:string would also give a result
  * (compound) `typeof x === "string"` -> x:string intended, at least in the code guarded by this predicate
  * (sequence) `x*y` and `x+z` -> x:num with very high likelyhood

TODO: Look into [Jan Vitek et al.: An analysis of the dynamic behavior of JavaScript programs](https://dl.acm.org/doi/pdf/10.1145/1806596.1806598?casa_token=k8dJKmYxdDQAAAAA:j9tOkPEY_ge_NHhKdDFwCNHQn-yvprFRtnCnJb5IvOQJm7EK0jt2NlP1mr7NUPBzZPozXu8chQIqnR4) to see if there is some useful heuristics we can use.

Oskar: This subfield (type inference based on dynamic analysis) seems to have been thoroughly explored beforehand. See
* [Trace Typing: An Approach for Evaluating Retrofitted Type Systems](https://drops.dagstuhl.de/opus/volltexte/2016/6095/)
* [JSTrace: Run-time Type Discovery for JavaScript](http://static.cs.brown.edu/research/pubs/theses/ugrad/2010/saftoiu.pdf)
* [Dynamic inference of static types for ruby](https://dl.acm.org/doi/abs/10.1145/1925844.1926437?casa_token=raqvsNKm37oAAAAA:bNdvboEFQMALD-QBLbWdH8xswXy0fkZu6BpGUliXYgg8-B1lkU8vvX0Vexo15N2_lMpRQRtV6kCZjUE)

I think what we can contribute in novelty is limited to the use of heuristics.

Therefore, I think it might be more beneficial to focus on the next problem.

#### Gaining high code coverage

My idea to solve this subproblem is the following:

* View the dynamic analysis as a way to generate constraints for the input parameters.
* Use the constraints to synthesize values that can drive the dynamic execution further.
* When the constraints are fully saturated, use an approach akin to symbolic execution to explore different branches.

In pseudocode:

```python
def rec(originalConstraints, symbolicExecutionIndex: int):
    for branchResult in (False, True):
        constraints = originalConstraints
        
        while True:
            argumentValues = synthesizeValues(constraints)
            # branchResult should also influence constraints somehow
            # The branch with index `symbolicExecutionIndex` is hardwired to return `branchResult`
            newConstraints = dynamicAnalysis(argumentValues)
            if newConstraints <= constraints:
                break
            constraints = newConstraints
		
        if symbolicExecutionIndex + 1 < numBranches:
            # are there more branches to explore?
        	rec(constraints, symbolicExecutionIndex + 1)
```

The output of this code is not specified.

Maybe we can join the constraints of different symbolic execution paths to generate a set of "super-constraints" that can be transformed into a type.

Or maybe it's easier to output the synthesized values as tests and have some other tool generate the types from these.

##### Postponed problems

* How do we handle functions that schedule actions on the event loop to run after the function returns?
  This includes async functions and functions that return promises.
* How do we discern between constructors and regular functions?
  Perhaps we can use the convention that constructors have names in CamelCase.
  Or we can check if the function assigns properties on `this`. This might also flag methods, though.

## Remarks (PT 20211129)

* what do you mean with *output not specified*?
  - I mean that displayed code computes something without returning a result. I.e. it is not specified how the computation can produce something useful.
* The main problem with all test-driven methods is that they compute under-approximations, even if we combine the results of several execution paths and argument variations. But at certain points, we liberally perform over-approximations, so that it is hard to argue formally about correctness in the end. In the end, we can only argue quantitatively by comparing against some benchmark (ground truth, at best).
* It would be best to reuse (and maybe improve) the transformation of traces to types and concentrate on improving coverage starting from as little as possible. Though any starting point should do - including example code.
  - Yes, I think this is a good approach. In this case the output of our tool would be a set of test cases that can be fed into the `dts-generate` tool, right?
* What's the issue with constructors vs regular functions?
  - Invoking a constructor as a regular method means that `this` is bound to the global object inside the constructor, so any property writes will be performed on the global object. Additionally the constructor returns `undefined` instead of an object if called without `new`.
