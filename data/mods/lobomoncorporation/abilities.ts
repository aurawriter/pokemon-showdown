export const Abilities: {[k: string]: ModdedAbilityData} = {
	fourthmatchflame:{
		onDamagingHit(damage, target, source, move) {
			if (!target.hp) {
				this.damage(source.baseMaxhp / 3, source, target, null, true);
			}
		},
		desc: "If this Pokemon is knocked out, that move's user loses 1/4 of its maximum HP, rounded down. If any active Pokemon has the Ability Damp, this effect is prevented.",
		shortDesc: "If this Pokemon is KOed, that move's user loses 1/4 its max HP.",
		name: "Fourth Match Flame",
},
	penitence:{
		onStart(pokemon) {
			for (const ally of pokemon.adjacentAllies()) {
				this.damage(target.baseMaxhp / 3, target, target);
				this.heal(ally.baseMaxhp / 3, ally, pokemon);
			}
		},
		name: "Penitence",
		rating: 0,
		num: 299,
	},
};
