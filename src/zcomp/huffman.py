import collections
import heapq
from typing import Dict, Tuple, Optional

class HuffmanNode:
    def __init__(self, symbol: Optional[int]=None, freq: int=0, left=None, right=None):
        self.symbol = symbol
        self.freq = freq
        self.left = left
        self.right = right

    def __lt__(self, other):
        # deterministic tie-breaking: compare freq, then symbol for leaves, then id
        if self.freq != other.freq:
            return self.freq < other.freq
        if (self.symbol is not None) and (other.symbol is not None):
            return self.symbol < other.symbol
        return id(self) < id(other)


class HuffmanCodec:
    def build_tree(self, data: bytes) -> Tuple[HuffmanNode, Dict[int,str]]:
        if not data:
            root = HuffmanNode()
            return root, {}
        counts = collections.Counter(data)
        pq = []
        for sym, f in counts.items():
            heapq.heappush(pq, (f, HuffmanNode(symbol=sym, freq=f)))
        if len(pq) == 1:
            # single symbol: give it code '0'
            f, node = heapq.heappop(pq)
            root = HuffmanNode()
            root.left = node
            codes = {node.symbol: '0'}
            return root, codes
        while len(pq) > 1:
            f1, n1 = heapq.heappop(pq)
            f2, n2 = heapq.heappop(pq)
            parent = HuffmanNode(freq=f1+f2, left=n1, right=n2)
            heapq.heappush(pq, (parent.freq, parent))
        root = heapq.heappop(pq)[1]
        codes = {}
        self._generate_codes(root, "", codes)
        return root, codes

    def _generate_codes(self, node: HuffmanNode, prefix: str, codes: Dict[int,str]):
        if node is None:
            return
        if node.symbol is not None:
            codes[node.symbol] = prefix or '0'
            return
        self._generate_codes(node.left, prefix + '0', codes)
        self._generate_codes(node.right, prefix + '1', codes)

    def encode(self, data: bytes) -> Tuple[bytes, Dict[int,int]]:
        root, codes = self.build_tree(data)
        writer = []
        for b in data:
            writer.append(codes[b])
        bits = ''.join(writer)
        # pack bits into bytes
        from .bitio import BitWriter
        bw = BitWriter()
        bw.write_bits(bits)
        payload = bw.get_bytes()
        # metadata: frequency table
        freq = collections.Counter(data)
        return payload, dict(freq)

    def decode(self, payload: bytes, freq_table: Dict[int,int], original_size: int) -> bytes:
        # rebuild tree from freq table
        import collections
        if not freq_table:
            return b""
        # build nodes similar to encode
        pq = []
        import heapq
        for sym, f in freq_table.items():
            heapq.heappush(pq, (f, HuffmanNode(symbol=sym, freq=f)))
        if len(pq) == 1:
            # single symbol repeated
            sym = pq[0][1].symbol
            return bytes([sym]) * original_size
        while len(pq) > 1:
            f1, n1 = heapq.heappop(pq)
            f2, n2 = heapq.heappop(pq)
            parent = HuffmanNode(freq=f1+f2, left=n1, right=n2)
            heapq.heappush(pq, (parent.freq, parent))
        root = heapq.heappop(pq)[1]
        # walk bits
        from .bitio import BitReader
        br = BitReader(payload)
        out = bytearray()
        node = root
        try:
            while len(out) < original_size:
                b = br.read_bit()
                node = node.left if b == 0 else node.right
                if node is None:
                    raise ValueError("Invalid bitstream")
                if node.symbol is not None:
                    out.append(node.symbol)
                    node = root
        except EOFError:
            raise ValueError("Unexpected EOF while decoding Huffman payload")
        return bytes(out)
