module.exports = {
    histogramBin: (data, nBins=20) => {
        if (!data.length) {
            return([]);
        }

        var bins = [];
        const sortedData = data.slice().sort((a, b) => a - b);
        const minValue = sortedData[0];
        const maxValue = sortedData[sortedData.length - 1];
        const interval = (maxValue - minValue) / nBins;

        var dataIx = 0;
        for(var i = 0; i < nBins; i++){
            const upperBound = minValue + (i + 1) * interval;
            var binCount = 0;
            while(dataIx < sortedData.length && sortedData[dataIx] <= upperBound) {
                binCount++;
                dataIx++;
            }
            bins.push({
                lower: minValue + i * interval,
                upper: upperBound,
                count: binCount});
        }

        return(bins);
    },
    rank: (data, point) => {
        return(data.filter(populationPoint => populationPoint > point).length + 1);
    },
    levenshtein: (a, b) => {
        const lengthA = a.length;
        const lengthB = b.length;
        const editDistances = Array(lengthB + 1).fill().map(() => Array(lengthA + 1).fill(-1));

        for (let i = 0; i <= lengthA; i++) {
            editDistances[0][i] = i;
        }

        for (let j = 0; j <= lengthB; j++) {
            editDistances[j][0] = j;
        }

        for (let i = 1; i <= lengthB; i++) {
            for (let j = 1; j <= lengthA; j++) {
                const cost = a[j-1] === b[i-1] ? 0 : 1;
                editDistances[i][j] = Math.min(editDistances[i-1][j] + 1,
                    Math.min(editDistances[i][j-1] + 1, editDistances[i-1][j-1] + cost));
            }
        }

        return editDistances[lengthB][lengthA];
    }
};