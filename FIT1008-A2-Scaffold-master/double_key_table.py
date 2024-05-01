from __future__ import annotations

from typing import Generic, TypeVar, Iterator
from data_structures.hash_table import LinearProbeTable, FullError
from data_structures.referential_array import ArrayR

K1 = TypeVar('K1')
K2 = TypeVar('K2')
V = TypeVar('V')


class DoubleKeyTable(Generic[K1, K2, V]):
    """
    Double Hash Table.

    Type Arguments:
        - K1:   1st Key Type. In most cases should be string.
                Otherwise `hash1` should be overwritten.
        - K2:   2nd Key Type. In most cases should be string.
                Otherwise `hash2` should be overwritten.
        - V:    Value Type.

    Unless stated otherwise, all methods have O(1) complexity.
    """

    # No test case should exceed 1 million entries.
    TABLE_SIZES = [5, 13, 29, 53, 97, 193, 389, 769, 1543, 3079, 6151, 12289, 24593, 49157, 98317, 196613, 393241,
                   786433, 1572869]

    HASH_BASE = 31

    def __init__(self, sizes: list | None = None, internal_sizes: list | None = None) -> None:
        if sizes is not None:
            self.TABLE_SIZES = sizes

        if internal_sizes is not None:
            self.internal_sizes = internal_sizes
        else:
            self.internal_sizes = self.TABLE_SIZES

        self.size_index = 0
        self.array: ArrayR[tuple[K1, V] | None] | None = ArrayR(self.TABLE_SIZES[self.size_index])
        self.count = 0

    def hash1(self, key: K1) -> int:
        """
        Hash the 1st key for insert/retrieve/update into the hashtable.

        :complexity: O(len(key))
        """

        value = 0
        a = 31417
        for char in key:
            value = (ord(char) + a * value) % self.table_size
            a = a * self.HASH_BASE % (self.table_size - 1)
        return value

    def hash2(self, key: K2, sub_table: LinearProbeTable[K2, V]) -> int:
        """
        Hash the 2nd key for insert/retrieve/update into the hashtable.

        :complexity: O(len(key))
        """

        value = 0
        a = 31417
        for char in key:
            value = (ord(char) + a * value) % sub_table.table_size
            a = a * self.HASH_BASE % (sub_table.table_size - 1)
        return value

    def _linear_probe(self, key1: K1, key2: K2 | None, is_insert: bool) -> tuple[int, int] | int:
        """
        Find the correct position for this key in the hash table using linear probing.

        :raises KeyError: When the key pair is not in the table, but is_insert is False.
        :raises FullError: When a table is full and cannot be inserted.

        len(key1): Length (or number of characters) of the top-level
        (1st) key.
        len(key2): Length (or number of characters) of the bottom-level
        (2nd) key.
        n: Array size in the top-level (1st) hash table.
        m: Array size in the bottom-level (2nd) hash table.
        comp==: Comparison operator for string equality.

        Time Complexity in terms of Setting an Item (__setitem__):
            Best: O(len(key1) + len(key2)), when the array position
            for top level (1st) key and bottom level (2nd) key is
            found in the expected positions of both top and
            bottom level hash tables based on the hash function.

            Worst: O(n + m), when both top and bottom level hash tables are full or
            nearly full as primary clustering occur.

        Time Complexity in terms of Obtaining an Item (__getitem__):
            Best: O(len(key1)), when the expected array position of the top level
            (1st) key of an item based on the hash function has no value inside
            it (None).

            Worst: O(n + m), when the bottom level (2nd) key of an item
            is not found in a full or nearly full bottom level hash
            table.

        Time Complexity in terms of Finding the Position of a Top Level Key:
            Best: O(len(key1)), when the expected array position of the top level
            (1st) key of an item based on the hash function has no value inside
            it (None).

            Worst: O(n), when the top level (1st) key of an item is not found in a
            full or nearly full top level hash table.
        """
        position_1 = self.hash1(key1)  # O(len(key1))
        position_2 = None

        # Traversing the top level hash table.
        for i in range(len(self.array)):  # O(n)

            # Checks if the array is None.
            if self.array[position_1] is None:
                if is_insert:
                    break
                else:
                    raise KeyError(key1)

            # Checks if the top level (1st) key is found.
            elif self.array[position_1][0] == key1:  # O(comp==)
                break

            elif i == len(self.array) - 1:
                raise FullError("Hash Table is full")

            else:
                position_1 = (position_1 + 1) % len(self.array)

        if is_insert and self.array[position_1] == None:
            self.array[position_1] = (key1, LinearProbeTable(self.internal_sizes))

            # Ensures any internal table uses the external hash2 for hashing keys
            self.array[position_1][1].hash = lambda key2, tab=self.array[position_1][1]: self.hash2(key2, tab)

        if key2 != None:
            position_2 = self.hash2(key2, self.array[position_1][1])  # O(len(key2))

            # Traversing the bottom level hash table.
            for j in range(len(self.array[position_1][1].array)):  # O(m)

                # Checks if the array is None.
                if self.array[position_1][1].array[position_2] is None:
                    if is_insert:
                        break
                    else:
                        raise KeyError(key2)

                        # Checks if the bottom level (2nd) key is found.
                elif self.array[position_1][1].array[position_2][0] == key2:
                    break

                elif j == len(self.array[position_1][1].array) - 1:
                    raise FullError("Internal Hash Table is full")

                else:
                    position_2 = (position_2 + 1) % len(self.array[position_1][1].array)
            return (position_1, position_2)

        else:
            return position_1

    def iter_keys(self, key: K1 | None = None) -> Iterator[K1 | K2]:
        """
        key = None:
            Returns an iterator of all top-level keys in hash table
        key = k:
            Returns an iterator of all keys in the bottom-hash-table for k.

        n: Array size of top level (1st) hash table.
        m: Array size of bottom level (2nd) hash table.
        len(key1): Length of the top level (1st) key.

        Time Complexity:
            Best: O(len(key1)), when the expected array position of the
            top level (1st) key of an item based on the hash function
            has no value inside it (None).

            Worst: O(n + m), when the top level (1st) key is found in
            full or nearly full top level hash table.
        """

        if key == None:
            for array in self.array:  # O(n)
                if array != None:
                    yield array[0]

        else:
            key1_position = self._linear_probe(key, None, False)
            for array in self.array[key1_position][1].array:  # O(m)
                if array != None:
                    yield array[0]

    def iter_values(self, key: K1 | None = None) -> Iterator[V]:
        """
        key = None:
            Returns an iterator of all values in hash table
        key = k:
            Returns an iterator of all values in the bottom-hash-table for k.

        n: Array size of top level (1st) hash table.
        m: Array size of bottom level (2nd) hash table.

        Time Complexity:
            Best: O(len(key1)), when the expected array position of the
            top level (1st) key of an item based on the hash function
            has no value inside it (None).

            Worst: O(n*m), when key (top level key) is null (None).
        """

        if key == None:
            for external_array in self.array:  # O(n)
                if external_array != None:
                    sub_table = external_array[1]
                    for internal_array in sub_table.array:  # O(m)
                        if internal_array != None:
                            yield internal_array[1]
        else:
            key1_position = self._linear_probe(key, None, False)
            for array in self.array[key1_position][1].array:  # O(m)
                if array != None:
                    yield array[1]

    def keys(self, key: K1 | None = None) -> list[K1 | K2]:
        """
        key = None: returns all top-level keys in the table.
        key = x: returns all bottom-level keys for top-level key x.

        n: Array size of top level (1st) hash table.
        m: Array size of bottom level (2nd) hash table.
        len(key1): Length of the top level (1st) key.

        Time Complexity:
            Best: O(len(key1)), when the expected array position of the
            top level (1st) key of an item based on the hash function
            has no value inside it (None).

            Worst: O(n + m), when the top level (1st) key is found in
            full or nearly full top level hash table.
        """
        key_lst = []
        if key == None:
            for array in self.array:  # O(n)
                if array != None:
                    key_lst.append(array[0])

        else:
            key1_position = self._linear_probe(key, None, False)
            for array in self.array[key1_position][1].array:  # O(m)
                if array != None:
                    key_lst.append(array[0])
        return key_lst

    def values(self, key: K1 | None = None) -> list[V]:
        """
        key = None: returns all values in the table.
        key = x: returns all values for top-level key x.

        n: Array size of top level (1st) hash table.
        m: Array size of bottom level (2nd) hash table.

        Time Complexity:
            Best: O(len(key1)), when the expected array position of the
            top level (1st) key of an item based on the hash function
            has no value inside it (None).

            Worst: O(n*m), when key (top level key) is null (None).
        """
        value_lst = []

        if key == None:
            for external_array in self.array:  # O(n)
                if external_array != None:
                    sub_table = external_array[1]
                    for internal_array in sub_table.array:  # O(m)
                        if internal_array != None:
                            value_lst.append(internal_array[1])
        else:
            key1_position = self._linear_probe(key, None, False)
            for array in self.array[key1_position][1].array:  # O(m)
                if array != None:
                    value_lst.append(array[1])
        return value_lst

    def __contains__(self, key: tuple[K1, K2]) -> bool:
        """
        Checks to see if the given key is in the Hash Table

        :complexity: See linear probe. (O(_linear_probe))
        """
        try:
            _ = self[key]
        except KeyError:
            return False
        else:
            return True

    def __getitem__(self, key: tuple[K1, K2]) -> V:
        """
        Get the value at a certain key

        :raises KeyError: when the key doesn't exist.
        """

        position1, position2 = self._linear_probe(key[0], key[1], False)
        return self.array[position1][1].array[position2][1]

    def __setitem__(self, key: tuple[K1, K2], data: V) -> None:
        """
        Set an (key, value) pair in our hash table.
        """

        key1, key2 = key
        position1, position2 = self._linear_probe(key1, key2, True)
        sub_table = self.array[position1][1]

        if sub_table.is_empty():
            self.count += 1

        sub_table[key2] = data

        # resize if necessary
        if len(self) > self.table_size / 2:
            self._rehash()

    def __delitem__(self, key: tuple[K1, K2]) -> None:
        """
        Deletes a (key, value) pair in our hash table.

        :raises KeyError: when the key doesn't exist.
        """
        position1, position2 = self._linear_probe(key[0], key[1], False)

        if len(self.array[position1][1]) == 1:
            self.array[position1] = None
            self.count -= 1

            position1 = (position1 + 1) % len(self.array)

            while not self.array[position1] is None:
                key1 = self.array[position1][0]
                sub_table = self.array[position1][1]
                for i in range(len(sub_table.array)):
                    if type(sub_table.array[i]) == tuple:
                        key2, value = sub_table.array[i][0], sub_table.array[i][1]
                        sub_table.array[i] = None
                        sub_table.count -= 1
                        self[(str(key1), str(key2))] = value
                position1 = (position1 + 1) % len(self.array)

        else:
            sub_table = self.array[position1][1]
            sub_table.array[position2] = None
            sub_table.count -= 1

            position2 = (position2 + 1) % len(sub_table.array)

            while not sub_table.array[position2] is None:
                item = sub_table.array[position2]
                sub_table.array[position2] = None
                sub_table.count -= 1
                sub_table[str(item[0])] = item[1]
                position2 = (position2 + 1) % len(sub_table.array)

    def _rehash(self) -> None:
        """
        Need to resize table and reinsert all values

        :complexity best: O(N*hash(K)) No probing.
        :complexity worst: O(N*hash(K) + N^2*comp(K)) Lots of probing.
        Where N is len(self)
        """
        self.size_index += 1
        old_array = self.array
        old_count = self.count
        self.array = ArrayR(self.TABLE_SIZES[self.size_index])
        self.count = 0

        for item1 in old_array:
            if item1 is not None:
                key1 = item1[0]
                sub_table = item1[1]
                old_count -= 1
                for item2 in sub_table.array:
                    if item2 is not None:
                        key2, value = item2[0], item2[1]
                        self[str(key1), str(key2)] = value
            if old_count == 0:
                break

    @property
    def table_size(self) -> int:
        """
        Return the current size of the table (different from the length)

        Time Complexity (Best and Worst): O(1)
        """
        return len(self.array)

    def __len__(self) -> int:
        """
        Returns number of elements in the hash table

        Time Complexity (Best and Worst): O(1)
        """
        return self.count

    def __str__(self) -> str:
        """
        String representation.

        Not required but may be a good testing tool.
        """
        dict_str = '{'
        for i in range(len(self.array)):
            if i != 0:
                dict_str += '     '

            if self.array[i] != None:
                dict_str += f"{self.array[i][0]}: "
                if self.array[i][1] != None:
                    for j in range(len(self.array[i][1].array)):
                        if type(self.array[i][1].array[j]) == tuple:
                            dict_str += f"({self.array[i][1].array[j][0]}, {self.array[i][1].array[j][1]})"
                        else:
                            dict_str += f"None"

                        if j == len(self.array[i][1].array) - 1:
                            break
                        else:
                            dict_str += ', '
                else:
                    dict_str += "None    "
            else:
                dict_str += "None: None"
        dict_str += '}'
        return dict_str


if __name__ == "__main__":
    test = DoubleKeyTable()
    print(test)
