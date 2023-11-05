export const Abilities: {[k: string]: ModdedAbilityData} = {
fourthmatchflame:{
		onDamagingHit(damage, target, source, move) {
			if (!target.hp) {
				this.damage(source.baseMaxhp / 3, source, target, null, true);
			}
		},
		desc: "If this Pokemon is knocked out, that move's user loses 1/3 of its maximum HP, rounded down. If any active Pokemon has the Ability Damp, this effect is prevented.",
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
			if (pokemon.side.totalFainted >= 2)
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
		desc: "This is a recording of the day we must never forget.",
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
			if(pokemon.baseSpecies.baseSpecies !== "176mhz")
			{
			this.damage(pokemon.baseMaxhp / 8, pokemon, pokemon);
			}
		},
		rating: 2,
		num: 152,
	},
	logging: {
		onSourceAfterFaint(length, target, source, effect) {
			if (effect && effect.effectType === 'Move') {
				this.heal(target.baseMaxhp / 3, source, source, this.dex.abilities.get('logging'))
			}
		},
		name: "Logging",
		desc: "This is a forest full of hearts. No matter how many he cuts down, the forest still remains dense.",
		rating: 3,
		num: 153,
	},
	forpeace: {
		onStart(source) {
			this.field.setTerrain('pitchblack');
		},
		name: "For Peace",
		desc: "A month later, we came to this conclusion: There was no such “beast” in the forest.",
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
		desc: "Blood covers the whole floor, screams echo, people are running away...",
		rating: -1,
		num: 54,
	},
	cursedfruit: {
		onDamagingHit(damage, target, source, move) {
			if (this.checkMoveMakesContact(move, source, target)) {
				if (this.randomChance(3, 10)) {
					source.trySetStatus('dzy', target);
				}
			}
		},
		name: "Cursed Fruit",
		desc: "The day a ripe apple fell off the tree in the garden where the princess and the king stood, the witch's heart shattered.",
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
		desc: "However, the curse continues eternally, never broken."
	},
	nightmareofchristmas: {
		onDamagingHit(damage, target, source, move) {
			this.field.setWeather('snow');
		},
		name: "Nightmare of Christmas",
		desc: "With my infinite hatred, I give you this gift.",
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
		desc: "I’ll hang his head over my bed. Only then can I get up in the morning without having a nightmare.",
		rating: 4.5,
		num: 255,
	},
	infectious: {
		name: "Infectious",
		desc: "If you feel an abdominal pain and a tingling sensation in your neck, the best thing you can do now is look at the great blue sky you'll never get to see again.",
		onDamagingHit(damage,target,source,move) {
			if (this.checkMoveMakesContact(move, source, target) && !source.status && source.runStatusImmunity('powder'))
			{
				if (target.getTypes().join() === 'Bug' || !target.setType('Bug')) return false;
				const infectRoll = this.random(100);
				if (infectRoll < 30)
				{
					this.add('-start', target, 'typechange', 'Bug');
				}
			}
		},
	},
	rhapsodyofmachine: {
		onModifyTypePriority: -1,
		onModifyType(move, pokemon) {
			if (move.flags['sound'] && !pokemon.volatiles['dynamax']) { // hardcode
				move.type = 'Steel';
			}
		},
		name: "Rhapsody of Machine",
		desc: "But nothing could compare to the music it makes when it eats a human.",
		rating: 1.5,
		num: 204,
	},
	bloodlust: {
		name: "Bloodlust",
		desc: "Many hands float in the bath. They are the hands of the people I once loved.",
		onModifyMove(move){
			if(move.flags['slicing']) {
				if(!move.drain) move.drain = [1 , 2];
			}
		},
	},
	adoration: {
		onBasePowerPriority: 24,
		onBasePower(basePower, attacker, defender, move) {
			if (attacker.gender && defender.gender) {
				if (attacker.gender !== defender.gender) {
					this.debug('Adoration boost');
					return this.chainModify(1.25);
				} else {
					this.debug('Adoration weaken');
					return this.chainModify(0.75);
				}
			}
		},
		name: "Adoration",
		desc: "...and my dear employees, I do hope you all put on the gas masks we distributed to you before we enter.",
		rating: 0,
		num: 79,
	},
	exuviae: {
		onDamagingHit(damage, target, source, move) {
			if (move.category === 'Special') {
				this.boost({spd: -1, spe: 2}, target, target);
			}
		},
		name: "Exuviae",
		desc: "It can enter your body through any aperture.",
		rating: 1,
		num: 133,
	},
	openedcan: {
		name: "Opened Can",
		desc: "Somewhere in the distance, you can hear seagulls.",
		onModifyMove(move) {
			if (!move.type === 'Water') return;
			if (!move.secondaries) {
				move.secondaries = [];
			}
			move.secondaries.push({
				chance: 30,
				status: 'dzy',
				ability: this.dex.abilities.get('Opened Can'),
			});
		},
	},
	dusttodust: {
		name: "Dust to Dust",
		desc: "Bearing the hope to return to dust, it shall go back to the grave with all that desires to live.",
		onDamagingHit(damage, target, source, move) {
			if (this.checkMoveMakesContact(move, source, target)) {
				if (this.randomChance(3, 10)) {
					source.trySetStatus('dsp', target);
				}
			}
		},
		rating: 1.5,
		num: 38,
	},
	hammerhead: {
		name: "Hammer Head",
		desc: "What's really pitiful is people like you dying to the likes of me.",
		onBasePower(basePower,attacker,defender,move){
			if(defender.hp == defender.maxhp)
			{
			return this.chainModify(1.5);
			}
		},
	},
	memoriesofscars: {
		onStart(pokemon) {
			let activated = false;
			for (const target of pokemon.adjacentFoes()) {
				if (!activated) {
					this.add('-ability', pokemon, 'memoriesofscars', 'boost');
					activated = true;
				}
				if (target.volatiles['substitute']) {
					this.add('-immune', target);
				} else {
					this.boost({spa: -1}, target, pokemon, null, true);
				}
			}
		},
		name: "Memories of Scars",
		desc: "Still, it didn’t matter to him. After all, he was “destined” to be a big bad wolf.",
		rating: 3.5,
		num: 22,
	},
};
