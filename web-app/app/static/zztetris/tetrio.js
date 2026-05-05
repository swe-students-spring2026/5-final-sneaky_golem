function PRNG(seed) {
	let _seed = parseInt(seed) % 2147483647;

	if (_seed <= 0) {
		_seed += 2147483646;
	}

	return {
		next: function () {
			return (_seed = (_seed * 16807) % 2147483647);
		},
		nextFloat: function (opt_minOrMax, opt_max) {
			return (this.next() - 1) / 2147483646;
		},
		shuffleArray: function (array) {
			let i = array.length;
			let j;

			if (i == 0) {
				return array;
			}

			while (--i) {
				j = Math.floor(this.nextFloat() * (i + 1));
				[array[i], array[j]] = [array[j], array[i]];
			}
			return array;
		},
		getCurrentSeed: function () {
			return _seed;
		},
	};
}

function generateTetrioQueue(seed, pieceCount) {
    num_bags = Math.ceil(pieceCount / 7);
	vo = { minotypes: ['z', 'l', 'o', 's', 'i', 'j', 't'] };
	rng = PRNG(seed);
	bag = [];
	for (i = 0; i < num_bags; i++) {
		e = [...vo.minotypes];
		rng.shuffleArray(e);
		bag.push(...e);
    }
    console.log(bag.join(""));
}
