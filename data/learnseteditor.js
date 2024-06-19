"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
// Import the Learnsets data from the learnsets.ts file
var learnsets_1 = require("./learnsets");
// Define a function to get the learnset of a given Pokemon
function getLearnset(pokemon) {
    // Check if Learnsets object is defined
    if (!learnsets_1.Learnsets) {
        console.log("Learnsets data is undefined.");
        return undefined;
    }
    // Convert the input to lowercase to match the keys in Learnsets
    var pokemonLower = pokemon.toLowerCase();
    // Check if the given Pokemon exists in Learnsets
    if (learnsets_1.Learnsets[pokemonLower]) {
        // Return the learnset of the given Pokemon
        return Object.keys(learnsets_1.Learnsets[pokemonLower].learnset);
    }
    else {
        // Return undefined if the given Pokemon does not exist
        console.log("Pokemon '" + pokemon + "' not found.");
        return undefined;
    }
}
// Example usage
var pokemonName = 'bulbasaur'; // Ensure input matches exactly as specified in learnsets.ts
var learnset = getLearnset(pokemonName);
if (learnset) {
    console.log("Learnset of " + pokemonName + ":");
    console.log(learnset);
}
//# sourceMappingURL=learnseteditor.js.map