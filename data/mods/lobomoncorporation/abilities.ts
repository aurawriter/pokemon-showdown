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
					this.debug("Found Arcana Beats");
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
		shortDesc: "Damaging static can spread to damaging enemies",
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
	logging: {
		onSourceAfterFaint(length, target, source, effect) {
			if (effect && effect.effectType === 'Move') {
				this.heal(pokemon.baseMaxhp / 3);
			}
		},
		name: "Logging",
		desc: "The Woodsman logs for hearts to heal itself with.",
		rating: 3,
		num: 153,
	},
	forpeace: {
		onStart(source) {
			this.field.setTerrain('pitchblack');
		},
		name: "For Peace",
		rating: 4,
		num: 229,
	},
	windup: {
		onStart(pokemon) {
			pokemon.removeVolatile('windup');
			if (pokemon.activeTurns && (pokemon.moveThisTurnResult !== undefined || !this.queue.willMove(pokemon))) {
				pokemon.addVolatile('windup');
			}
		},
		onBeforeMovePriority: 9,
		onBeforeMove(pokemon) {
			if (pokemon.removeVolatile('windup')) {
				this.add('cant', pokemon, 'ability: Windup');
				return false;
			}
			pokemon.addVolatile('windup');
		},
		onBasePower(basePower,attacker,defender,move){
			return this.chainModify(1.5);
		},
		condition: {},
		name: "Windup",
		desc: "Moves deal more damage but have to windup every other turn",
		rating: -1,
		num: 54,
	},
	cursedfruit: {
		onDamagingHit(damage, target, source, move) {
			if (this.checkMoveMakesContact(move, source, target)) {
				if (this.randomChance(3, 10)) {
					source.trySetStatus('slp', target);
				}
			}
		},
		name: "Cursed Fruit",
		rating: 1.5,
		num: 38,
	},
	fullbloom: {
		onDamagingHit(damage, target, source, move) {
			if (!target.hp) {
				if(source){
					source.transformInto(target, this.dex.abilities.get('fullbloom'));
				}
			}
		},
		name: "Full Bloom",
		desc: "When Beauty and the Beast dies, its curse continues"
	},
	nightmareofchristmas: {
		onDamagingHit(damage, target, source, move) {
			this.field.setWeather('snow');
		},
		name: "Nightmare of Christmas",
		rating: 1,
		num: 245,
	},
	deadoralive: {
		onStart(pokemon) {
			pokemon.abilityState.choiceLock = "";
		},
		onBeforeMove(pokemon, target, move) {
			if (move.isZOrMaxPowered || move.id === 'struggle') return;
			if (pokemon.abilityState.choiceLock && pokemon.abilityState.choiceLock !== move.id) {
				// Fails unless ability is being ignored (these events will not run), no PP lost.
				this.addMove('move', pokemon, move.name);
				this.attrLastMove('[still]');
				this.debug("Disabled by Dead or Alive");
				this.add('-fail', pokemon);
				return false;
			}
		},
		onModifyMove(move, pokemon) {
			if (pokemon.abilityState.choiceLock || move.isZOrMaxPowered || move.id === 'struggle') return;
			pokemon.abilityState.choiceLock = move.id;
		},
		onModifySpePriority: 1,
		onModifySpe(spe, pokemon) {
			if (pokemon.volatiles['dynamax']) return;
			// PLACEHOLDER
			this.debug('Dead or Alive speed boost');
			return this.chainModify(1.5);
		},
		onDisableMove(pokemon) {
			if (!pokemon.abilityState.choiceLock) return;
			if (pokemon.volatiles['dynamax']) return;
			for (const moveSlot of pokemon.moveSlots) {
				if (moveSlot.id !== pokemon.abilityState.choiceLock) {
					pokemon.disableMove(moveSlot.id, false, this.effectState.sourceEffect);
				}
			}
		},
		onEnd(pokemon) {
			pokemon.abilityState.choiceLock = "";
		},
		name: "Dead or Alive",
		rating: 4.5,
		num: 255,
	},
};
