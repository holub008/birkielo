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
        return(data.filter(populationPoint => populationPoint > point).length);
    },
};