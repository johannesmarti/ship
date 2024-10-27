export function moveElement(array, fromOffset, toOffset) {
  console.assert(Array.isArray(array), `first argument needs to be an array`);
  console.assert(fromOffset < array.length, `first argument needs be an index in the array`);
  console.assert(toOffset <= array.length, `second argument needs to be
an index in the array, or the length of the array`);
  const mover = array[fromOffset];
  if (fromOffset < toOffset) {
    return [...array.slice(0, fromOffset),
            ...array.slice(fromOffset + 1, toOffset), mover,
            ...array.slice(toOffset)];
  } else {
    return [...array.slice(0, toOffset), mover,
            ...array.slice(toOffset, fromOffset),
            ...array.slice(fromOffset + 1)];
  }
}
