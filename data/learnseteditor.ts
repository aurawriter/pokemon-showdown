// Import the Learnsets data from the learnsets.ts file
import { Learnsets } from './learnsets';

// Define a function to get the learnset of a given Pokemon
function getLearnset(pokemon: string): string[] | undefined {
	// Check if Learnsets object is defined
	if (!Learnsets) {
		console.log("Learnsets data is undefined.");
		return undefined;
	}

	// Convert the input to lowercase to match the keys in Learnsets
	const pokemonLower = pokemon.toLowerCase();

	// Check if the given Pokemon exists in Learnsets
	if (Learnsets[pokemonLower]) {
		// Return the learnset of the given Pokemon
		return Object.keys((Learnsets[pokemonLower] as any).learnset);
	} else {
		// Return undefined if the given Pokemon does not exist
		console.log(`Pokemon '${pokemon}' not found.`);
		return undefined;
	}
}

// Example usage
const pokemonName = 'bulbasaur'; // Ensure input matches exactly as specified in learnsets.ts
const learnset = getLearnset(pokemonName);

if (learnset) {
	console.log(`Learnset of ${pokemonName}:`);
	console.log(learnset);
}
