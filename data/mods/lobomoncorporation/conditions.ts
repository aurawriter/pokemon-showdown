export const Conditions: {[id: string]: ModdedConditionData} = {
//Pitch Black
	pitchblack: {
		name: 'PitchBlack',
		effectType: 'Weather',
		duration: 5,
	   durationCallback(source,effect){
			if(source?.hasItem('darkrock')){
				return 8;
			}
			return 5;
		},
		onWeatherModifyDamage(damage, attacker, defender, move) {
			if (move && defender.getMoveHitData(move).typeMod > 0) {
				return this.chainModify(1.5);
			}
			if(move.type === 'Psychic') {
				return this.chainModify(0.5);
			}
		},
		onFieldStart(field, source, effect) {
			if (effect?.effectType === 'Ability') {
				if (this.gen <= 5) this.effectState.duration = 0;
				this.add('-weather', 'PitchBlack', '[from] ability: ' + effect.name, '[of] ' + source);
			} else {
				this.add('-weather', 'PitchBlack');
			}
		},
		onFieldResidualOrder: 1,
		onFieldResidual() {
			this.add('-weather', 'PitchBlack', '[upkeep]');
			this.eachEvent('Weather');
		},
		onFieldEnd() {
			this.add('-weather', 'none');
		},
	},
//Frostbite
	fbt: {
		name: 'fbt',
		effectType: 'Status',
		onStart(target, source, sourceEffect) {
			if (sourceEffect && sourceEffect.id === 'frostorb') {
				this.add('-status', target, 'fbt', '[from] item: Frost Orb');
			} else if (sourceEffect && sourceEffect.effectType === 'Ability') {
				this.add('-status', target, 'fbt', '[from] ability: ' + sourceEffect.name, '[of] ' + source);
			} else { 
				this.add('-status', target, 'fbt');
			}
		},
		// Damage reduction is handled directly in the sim/battle.js damage function
		onResidualOrder: 10,
		onResidual(pokemon) {
			this.damage(pokemon.baseMaxhp / 16);
		},
		start: "  [POKEMON] was frostbitten!",
		startFromItem: "  [POKEMON] was frostbitten by the [ITEM]!",
		alreadyStarted: "  [POKEMON] is already frosbitten!",
		end: "  [POKEMON]'s frostbite was healed!",
		endFromItem: "  [POKEMON]'s [ITEM] healed its frostbite!",
		damage: "  [POKEMON] was hurt by its frostbite!",

	},
//Despair
	dsp: {
		name: 'dsp',
		effectType: 'Status',
		onStart(target, source, sourceEffect) {
			if (sourceEffect && sourceEffect.effectType === 'Ability') {
				this.add('-status', target, 'dsp', '[from] ability: ' + sourceEffect.name, '[of] ' + source);
			} else {
				this.add('-status', target, 'dsp');
			}
		},
		onModifySpD(spd, pokemon) {
			// Paralysis occurs after all other Speed modifiers, so evaluate all modifiers up to this point first
			spd = this.finalModify(spd);
			spd = Math.floor(spd * 50 / 100);
			return spd;
		},
		onBeforeMovePriority: 1,
		onBeforeMove(pokemon) {
			if (this.randomChance(1, 4)) {
				this.add('cant', pokemon, 'dsp');
				return false;
			}
		},
		start: "  [POKEMON] is filled with despair! It may be unable to move!",
		alreadyStarted: "  [POKEMON] is already filled with despair!",
		end: "  [POKEMON] found hope once more!",
		endFromItem: "  [POKEMON]'s [ITEM] filled it with hope!",
		cant: "[POKEMON] is despaired! It can't move!",

},
	par: {
		name: 'par',
		effectType: 'Status',
		onStart(target, source, sourceEffect) {
			if (sourceEffect && sourceEffect.effectType === 'Ability') {
				this.add('-status', target, 'par', '[from] ability: ' + sourceEffect.name, '[of] ' + source);
			} else {
				this.add('-status', target, 'par');
			}
		},
		onModifySpe(spe, pokemon) {
			// Paralysis occurs after all other Speed modifiers, so evaluate all modifiers up to this point first
			spe = this.finalModify(spe);
			if (!pokemon.hasAbility('quickfeet')) {
				spe = Math.floor(spe * 50 / 100);
			}
			return spe;
		},
		/* onBeforeMovePriority: 1,
		onBeforeMove(pokemon) {
			if (this.randomChance(1, 4)) {
				this.add('cant', pokemon, 'par');
				return false; 
			} 
		}, */
	},
		dzy: {
		name: 'dzy',
		effectType: 'Status',
		onStart(target, source, sourceEffect) {
			if (sourceEffect && sourceEffect.effectType === 'Ability') {
				this.add('-status', target, 'dzy', '[from] ability: ' + sourceEffect.name, '[of] ' + source);
			} else {
				this.add('-status', target, 'dzy');
			}
		},
		onModifyDef(def, pokemon) {
			def = this.finalModify(def);
			def = Math.floor(def * 50 / 100);
			return def;
		},
		onBeforeMovePriority: 1,
		onBeforeMove(pokemon) {
			if (this.randomChance(1, 4)) {
				this.add('cant', pokemon, 'dzy');
				return false;
			}
		},
		start: "  [POKEMON] is drowsy! It may be unable to move!",
		alreadyStarted: "  [POKEMON] is already drowsy!",
		end: "  [POKEMON] is awake!",
		endFromItem: "  [POKEMON]'s [ITEM] woke it up!",
		cant: "[POKEMON] is drowsy! It can't move!",

},
};
