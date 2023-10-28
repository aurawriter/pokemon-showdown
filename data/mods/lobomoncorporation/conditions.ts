export const Conditions: {[id: string]: ModdedConditionData} = {
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
};
