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
	standardtraining:{
		desc: "This Pokemon is very good for training.",
		shortDesc: "No effect.",
		name: "Standard Training",
	},
	pilingstory: {
		onResidualOrder: 28,
		onResidualSubOrder: 2,
		onResidual(pokemon) {
			if (!pokemon.hp) return;
			for (const target of pokemon.foes()) {
				if (target.status === 'dsp') {
					this.damage(target.baseMaxhp / 8, target, pokemon);
				}
			}
		},
		name: "Piling Story",
		desc: "This Pokemon deals damage every turn to Pokemon suffering from Despair",
		shortDesc: "Despairing Pokemon take damage every turn",
		rating: 1.5,
		num: 123,
	},
	loveandhate: {
		onStart(pokemon) {
			if(pokemon.species.baseSpecies!=='Queen of Hatred' || pokemon.transformed) return;
			if (pokemon.side.totalFainted >= 0)
			{
				this.debug("Enough Pokemon are fainted! Transforming!");
				pokemon.formeChange("Queen of Hatred-Breach");
				const beatsIndex = pokemon.moves.indexOf('arcanabeats');
				if(beatsIndex < 0) return false;
				else{
					debug.log("Found Arcana Beats");
				pokemon.moveSlots[beatsIndex]={
							move: 'Arcana Slave',
							id: 'arcanaslave',
							pp: 10,
							maxpp: 10,
							flags: {charge: 1},
							target: "normal",
							disabled: false,
							used: false,
							virtual: true,
						}
					}
				}
			},
		name: "Love and Hate",
		desc: "Queen of Hatred transforms when at least 2 allied Pokemon are fainted",
	},
	bearpaws: {
		// upokecenter says this is implemented as an added secondary effect
		onModifyMove(move) {
			if (!move?.flags['contact'] || move.target === 'self') return;
			if (!move.secondaries) {
				move.secondaries = [];
			}
			move.secondaries.push({
				chance: 30,
				status: 'dsp',
				ability: this.dex.abilities.get('bearpaws'),
			});
		},
		name: "Bear Paws",
		shortDesc: "Teddy Bear's loneliness has a chance of spreading",
		rating: 2,
		num: 143,
	},
	noise: {
		name: "Noise",
		onDamagingHit(damage, target, source, move) {
			const sourceAbility = source.getAbility();
			if (sourceAbility.isPermanent || sourceAbility.id === 'mummy') {
				return;
			}
			if (this.checkMoveMakesContact(move, source, target, !source.isAlly(target))) {
				const oldAbility = source.setAbility('mummy', target);
				if (oldAbility) {
					this.add('-activate', target, 'ability: Mummy', this.dex.abilities.get(oldAbility).name, '[of] ' + source);
				}
			}
		},
		onResidual(pokemon) {
			this.damage(pokemon.baseMaxhp / 8, pokemon, pokemon);
		},
		rating: 2,
		num: 152,
	},
};
