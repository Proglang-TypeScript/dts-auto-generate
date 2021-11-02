# dts-auto-generate

## Goal

We want to generate TypeScript declaration files for JavaScript libraries **without** relying on pre-written code examples.

Using such code examples are problematic because they are:

* Non-exhaustive. The library might contain additional exported functions that are not shown in the code examples. The functions that are shown in the examples may also have behaviours that are not properly explained in the code. (I imagine that) functions with many configuration options suffer a lot from this.
* Stale. Code examples are not a part of the shipped library. Instead they serve as documentation. (From studies we know that) documentation material is susceptible to becoming stale, just as well as manually written TS declaration files (see e.g. TSEvolve).

## Possible approaches

### Static analysis of the JavaScript library

Pros: Does not require code examples by design.

Cons: Requires development of a custom, lightweight static analysis. Current "general" static analysis tools for JS do not scale well (I think). It might also be hard to get a sufficient degree of precision.

See e.g.: [TSInfer](https://cs.au.dk/~amoeller/papers/tstools/), which is a continuation of TSCheck.
I think we will have a hard time with implementing a *better* static analysis than what they use in TSInfer. Maybe we could improve upon their work, but in that case I think it would be hard to argue for novelty.
We should evaluate our results against TSInfer's to show that we can infer more precise results than with static analysis!

### Machine learning

We can use the JavaScript library code as data and the corresponding TS declaration files as targets. Maybe there are enough pairs to enable some kind of machine learning approach.

Pros: Will figure out type inference heuristics automatically.

Cons: I have little experience with machine learning algorithms and their applications. The toughest problem will probably be to encode JavaScript code into a suitable format.

TODO: Look for related work exploring this direction.

[NL2Type: Inferring JavaScript Function Types from Natural Language Information](https://ieeexplore.ieee.org/document/8811893) uses parameter names, function names and documentation (comments) to infer types.

### Combined "symbolic execution" and dynamic analysis

We can build on the original dynamic analysis idea of *dts-generate*. We will add some way to automatically generate interesting test cases or otherwise explore the library code with good coverage. Based on the dynamically observed *interactions* we can infer types.

Pros: We can reuse a lot of infrastructure from the *dts-generate* project. We do not have to implement a JavaScript (abstract) interpreter.

Cons: The quality of the output will rely a lot on how well we can exercise the library code.

We do not want to do standard symbolic execution, as this would require us to implement a JavaScript interpreter.

The current *dts-generate* approach does (to my understanding) use the runtime types of argument values for type inference in a lot of cases. We do not have access to such values in our case, so type inference should be based solely on usage (patterns).
*dts-generate* also assumes that the code examples represent valid uses of the library. We will likely end up exploring code paths that correspond to error handling (due to e.g. wrong argument types) or otherwise unintended usage of the functions.

In Jalangi2 there is an option to override the result of conditions. This gives an easy way to recursively explore all possible branches in the code. Aside from the path explosion problem, you also encounter the issue that you are exploring branching pairs that are impossible in practice. Maybe an SMT solver could be used to figure out when branch combinations are invalid, but due to JavaScript's dynamic nature, I think this would be extremely difficult.
Perhaps the impact of exploring invalid branch combinations is not that high for type inference.

[TSTest](https://cs.au.dk/~amoeller/papers/tstest/) is a relevant tool/paper on how to generate tests for JavaScript libraries based on TypeScript declaration files. The tool essentially generates function arguments based on the declared types, runs the functions, and then checks whether the return value matches the type specified in the declaration file.

[Python probabilistic type inference with natural language support](https://dl.acm.org/doi/abs/10.1145/2950290.2950343) combines a machine learning algorithm for learning types based on variable names with "probabilistic inference" based on data-flow, attribute accesses and explicit type checks.
The presentation is mathematically detailed.
We should be careful that our work does not end up as a worse version of this.

