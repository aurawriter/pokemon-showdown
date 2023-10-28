export const Conditions: {[id: string]: ModdedConditionData} = {
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
		
		onModifySpD(spe, pokemon) {
			// Paralysis occurs after all other Speed modifiers, so evaluate all modifiers up to this point first
			spd = this.finalModify(spd);
			spd = Math.floor(spd * 50 / 100);
			return spd;
		},
		onModifyDef(def, pokemon) {
			def = this.finalModify(def);
			def = Math.floor(def * 50 / 100);
			return def;
		},
		onBeforeMovePriority: 1,
		onBeforeMove(pokemon) {
			if (this.randomChance(1, 4)) {
				this.add('cant', pokemon, 'dsp');
				return false;
			}
		},
};
