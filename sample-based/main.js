#!/usr/bin/env node

// https://stackoverflow.com/a/31194949/1098680
function $args(func) {
    return (func + '')
      .replace(/[/][/].*$/mg,'') // strip single-line comments
      .replace(/\s+/g, '') // strip white space
      .replace(/[/][*][^/*]*[*][/]/g, '') // strip multi-line comments
      .split('){', 1)[0].replace(/^[^(]*[(]/, '') // extract the parameters
      .replace(/=[^,]+/g, '') // strip any ES6 defaults
      .split(',').filter(Boolean); // split & filter [""]
}

const process = require('process');
const argv = process.argv;

if(argv.length < 4) {
	throw new Error(`${argv.length} < 4, missing MOD_PATH AND MOD_NAME`);
}

const MOD_PATH = argv[2],
	  MOD_NAME = argv[3];

const fs = require('fs');
const path = require('path');

const types = [
	{name: 'undefined', values: [undefined]},
	//{name: 'null', values: [null]},
	{name: 'boolean', values: [false, true]},
	{name: 'number', values: [-1, 0, 1]},
	{name: 'string', values: ['', 'teststring']},
	{name: 'object', values: [{}]},
	{name: 'array', values: [[], [1, 2, 3]]},
];

const mod = require(require.resolve(MOD_NAME, {paths: [MOD_PATH]}));

// Interpret exception as invalid input
const works = (input) => {
	try { return [true, mod(input)]; }
	catch(e) { return [false, e]; }
};

const workingTypes = [];
for(const {name, values} of types) {
	const results = values.map(works);
	if(results.some(([ok, _]) => !ok)) continue;

	const returnedValues = new Set(results.map(([_, ret]) => ret));
	workingTypes.push({name, returns: [...returnedValues]});
}

if(workingTypes.length == 0) {
	console.log(`${MOD_NAME} does not exit without an exception for any of our provided types`);
	return;
}

const returnTypeToArgType = {};
for(const {name, returns} of workingTypes) {
	for(const retVal of returns) {
		const retType = typeof retVal;
		if(!(retType in returnTypeToArgType))
			returnTypeToArgType[retType] = new Set();

		returnTypeToArgType[retType].add(name);
	}
}

for(const [retType, argTypes] of Object.entries(returnTypeToArgType)) {
	const optional = argTypes.delete('undefined');
	let typeStr = [...argTypes].join(' | ');
	if(optional) {
		if(argTypes.size == 1) typeStr += '?';
		else typeStr = `(${typeStr})?`;
	}

	console.log(`function ${MOD_NAME}(${$args(mod)[0]}: ${typeStr}) -> ${retType}`);
}

// TODO: This is considered bad practice, but I don't know how we're supposed to exit
// otherwise, as the library might set up things to run on the event loop.
const t = setTimeout(() => process.exit(0), 1000);
t.unref();
