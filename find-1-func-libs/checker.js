const process = require('process');
const argv = process.argv;

if(argv.length < 4) {
	throw new Error(`${argv.length} < 4, missing MOD_PATH AND MOD_NAME`);
}

const MOD_PATH = argv[2],
	  MOD_NAME = argv[3];

// Load the module named MOD_NAME from MOD_PATH
const mod = require(require.resolve(MOD_NAME, {paths: [MOD_PATH]}));

// Then check if the module is a single-function module with one argument.

if(typeof mod !== 'function')
	throw new Error('Module is not function-typed');

if(mod.length > 1)
	throw new Error('Module function has more than one declared argument');

if(Object.values(mod).length !== 0)
	throw new Error('Additional properties are attached to module function');
