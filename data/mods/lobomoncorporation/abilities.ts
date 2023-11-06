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
		shortDesc: "This Pokemon is very good for training. No effect.",
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
		desc: "On switch in, Queen of Hatred transforms when at least 2 allied Pokemon are fainted",
	},
	bearpaws: {
		// upokecenter says this is implemented as an added secondary effect
		onModifyMove(move) {
			if (!move?.flags['contact'] || move.target === 'self') return;
			if (!move.secondaries) {
				move.secondaries = [];
			}
			move.secondaries.push({
				chance: 100,
				status: 'dsp',
				ability: this.dex.abilities.get('bearpaws'),
			});
		},
		name: "Bear Paws",
		shortDesc: "This Pokemon's contact moves have a 30% chance of inflicting despair.",
		rating: 2,
		num: 143,
	},
	noise: {
		name: "Noise",
		desc: "This is a recording of the day we must never forget.",
		shortDesc: "Damaging static can spread to enemies that damage 1.76.",
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
		desc: "This Pokemon is healed ⅓ of its health if it attacks and KOes another Pokemon.",
		rating: 3,
		num: 153,
	},
	forpeace: {
		onStart(source) {
			this.field.setTerrain('pitchblack');
		},
		name: "For Peace",
		desc: "On switch-in, this Pokemon summons Pitch Black",
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
		desc: "This Pokemon skips every other turn, but its moves are powered up 50%",
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
		desc: "30% chance a Pokemon making contact with this Pokemon will become drowsy.",
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
		desc: "When this Pokemon is KO’d, the opponent is transformed into it."
	},
	nightmareofchristmas: {
		onDamagingHit(damage, target, source, move) {
			this.field.setWeather('snow');
		},
		name: "Nightmare of Christmas",
		desc: "When this Pokemon is hit by an attack, the effect of Snow begins.",
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
		desc: "30% chance a Pokemon making contact with this Pokemon will be turned into a Bug-type.",
		onDamagingHit(damage,target,source,move) {
			if (this.checkMoveMakesContact(move, source, target) && !source.status && source.runStatusImmunity('powder'))
			{
				if (target.getTypes().join() === 'Bug' || !target.setType('Bug')) return false;
				const infectRoll = this.random(100);
				if (infectRoll < 100)
				{
					this.add('-start', source, 'typechange', 'Bug');
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
		desc: " This Pokemon's sound-based moves become Steel type.",
		rating: 1.5,
		num: 204,
	},
	bloodlust: {
		name: "Bloodlust",
		desc: "This Pokemon’s slicing moves recover 50% of the damage dealt.",
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
		desc: "This Pokemon's attacks do 1.25x on opposite gender targets; 0.75x on same gender.",
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
		desc: " If a special attack hits this Pokemon, Special Defense is lowered by 1, Speed is raised by 2.",
		rating: 1,
		num: 133,
	},
	openedcan: {
		name: "Opened Can",
		desc: "This Pokemon’s Water-type moves have a 30% chance to cause the target to become drowsy.",
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
		desc: "30% chance a Pokemon making contact with this Pokemon will be filled with despair.",
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
		desc: "If the target is at 100% HP, moves do 50% more damage.",
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
		desc: "On switch-in, this Pokemon lowers the Special Attack of opponents by 1 stage.",
		rating: 3.5,
		num: 22,
	},
	youruniverse: {
		onModifyPriority(priority, pokemon, target, move) {
			if (move.flags['heal']) {
				move.universeBoosted = true;
				return priority + 1;
			}
		},
		name: "Your Universe",
		desc: "This Pokemon's healing moves have their priority raised by 1.",
		rating: 4,
		num: 158,
	},
	darkdash: {
		onModifySpe(spe, pokemon) {
			if (this.field.isWeather(['PitchBlack'])) {
				return this.chainModify(2);
			}
		},
		name: "Dark Dash",
		desc: "If Pitch Black is active, this Pokemon's Speed is doubled.",
		rating: 3,
		num: 202,
	},
};
