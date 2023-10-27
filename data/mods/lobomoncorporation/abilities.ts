export const Abilities: {[k: string]: ModdedAbilityData} = {
fourthmatchflame:{
		onDamagingHit(damage, target, source, move) {
			if (!target.hp) {
				this.damage(source.baseMaxhp / 3, source, target, null, true);
			}
		},
		desc: "If this Pokemon is knocked out, that move's user loses 1/4 of its maximum HP, rounded down. If any active Pokemon has the Ability Damp, this effect is prevented.",
		shortDesc: "Scorched Girl explodes when she faints",
		name: "Fourth Match Flame",
	},
penitence:{
		onStart(pokemon) {
			for (const ally of pokemon.adjacentAllies()) {
				this.damage(pokemon.baseMaxhp / 3, pokemon, pokemon);
				this.heal(ally.baseMaxhp / 3, ally, pokemon);
			}
		},
		desc: "On switch-in, for each ally, this Pokemon loses 1/3 of its HP to heal them 1/3 of their HP.",
		shortDesc: "One Sin loses HP to heal allies.",
		name: "Penitence",
		rating: 0,
		num: 299,
	},
	frostsplinter:{
		onModifyMove(move)
		{
		if(!(move.type === 'Ice')||move.category === 'Status') return;
		if(!move.secondaries){
			move.secondaries = [];
		}
		move.secondaries.push({
				boosts: {
					spe: -1,
				},
				ability: this.dex.abilities.get('frostsplinter'),
			});
		},
		desc: "This Pokemon's Ice type move's slow down its target.",
		shortDesc: "Snow Queen's Ice-type moves slow down her victims.",
		name: "Frost Splinter",
	},
};
