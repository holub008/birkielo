export async function callBackend(endpoint) {
    const response = await fetch(endpoint);
    var data = {};
    try {
        data = await response.json();
    }
    catch (error) {
        console.log(error);
        console.log(response);
    }
    if (response.status !== 200) throw Error(response);

    return data;
}

export function isEmpty(obj){
    return (Object.keys(obj).length === 0 && obj.constructor === Object);
}