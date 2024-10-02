import { Hierarchization, Position } from './hierarchization.mjs'
import { Schema } from './schema.mjs'

function arraysAreEqual(arr1, arr2) {
  // This chatGPT code might might be wrong in case arr1 has undefined
  // entries. It works for now
  return arr1.length === arr2.length &&
            arr1.every((value, index) => value === arr2[index]);
}

const schema = Schema.fromJSON([
  {
    "name": "dim 1 with 3 entries",
    "indices": ["1.1", "1.2", "1.3"]
  },
  {
    "name": "dim 2 with 5 entries",
    "indices": ["2.1", "2.2", "2.3", "2.4", "2.5"]
  },
  {
    "name": "dim 3 with 2 entries",
    "indices": ["3.1", "3.2"]
  },
  {
    "name": "dim 4 with 3 entries",
    "indices": ["4.1", "4.2", "4.3"]
  },
  {
    "name": "dim 5 with 4 entries",
    "indices": ["5.1", "5.2", "5.3", "5.4"]
  }
]);

let hierarchization = Hierarchization.create([], [0,1,2], [3,4])

hierarchization.checkAgainstSchema(schema);
console.assert(arraysAreEqual(hierarchization.absoluteAddress([1, 3, 3], [7, 0]),
                              [1, 3, 3, 7, 0]),
  "absoluteAddress is reasonable");

console.assert(hierarchization.isMovable(Position.row(2), Position.fixed(0)),
  "movable from row hierarchy to fixed");
console.assert(hierarchization.isMovable(Position.column(1), Position.fixed(0)),
  "movable from column hierarchy to fixed");
console.assert(hierarchization.isMovable(Position.column(0), Position.column(2)),
  "movable inside of column hierarchy to fixed");
console.assert(!hierarchization.isMovable(Position.column(0), Position.column(1)),
  "not movable inside of column hierarchy to higher");
console.assert(!hierarchization.isMovable(Position.column(0), Position.column(0)),
  "not movable inside of column hierarchy on same");

hierarchization = hierarchization.move(Position.column(1), Position.fixed(0), 2);
// hierarchization = new Hierarchization([(4,2)], [0,1,2], [3])
console.assert(arraysAreEqual(hierarchization.absoluteAddress([1, 3, 3], [7]),
                              [1, 3, 3, 7, 2]),
  "absoluteAddress with fixed is reasonable");

const json = hierarchization.toPlainJSON();
const reconstructed = Hierarchization.fromPlainJSON(json);
console.assert(reconstructed._fixed.length === 1,
  "reconstructed.fixed has right length");
console.assert(reconstructed._fixed[0].order() === 4,
  "reconstructed.fixed has right order");
console.assert(reconstructed._fixed[0].fixedIndex() === 2,
  "reconstructed.fixed has right fixedIndex");
console.assert(arraysAreEqual(hierarchization._rowHierarchy, reconstructed._rowHierarchy),
  "reconstructed has same rowHierarchy");
console.assert(arraysAreEqual(hierarchization._columnHierarchy, reconstructed._columnHierarchy),
  "reconstructed has same columnHierarchy");

hierarchization = hierarchization.move(Position.column(0), Position.row(1), 1);
// hierarchization = new Hierarchization([(4,2)], [0,3,1,2], [])
console.assert(hierarchization.isMovable(Position.fixed(0), Position.column(0)),
  "can move fixed to empty");
console.assert(!hierarchization.isMovable(Position.fixed(0), Position.row(0)),
  "can not empty fixed orders");

hierarchization = hierarchization.move(Position.fixed(0), Position.column(0), 2);
// hierarchization = new Hierarchization([], [0,3,1,2], [4])
console.assert(hierarchization.isMovable(Position.column(0), Position.fixed(0)),
  "can move singleton to fixed");
console.assert(!hierarchization.isMovable(Position.column(0), Position.row(0)),
  "can not empty row if fixed is empty");

hierarchization = hierarchization.move(Position.row(2), Position.row(1), 0);
// hierarchization = new Hierarchization([], [0,1,3,2], [4])
console.assert(arraysAreEqual(hierarchization.absoluteAddress([1, 3, 4, 7], [0]),
                              [1, 3, 7, 4, 0]),
  "absoluteAddress after internal move is reasonable");
