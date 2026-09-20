import test from 'node:test';
import assert from 'node:assert/strict';

test('source URL boundary rejects internal, reserved, encoded and mixed DNS targets', async () => {
  const { publicAddress, resolvePublicUrl, htmlToText } = await import('./public-source.ts');
  for (const ip of ['127.0.0.1','10.0.0.1','172.16.1.1','192.168.1.1','169.254.169.254','100.64.0.1','0.0.0.0','198.18.0.1','192.0.2.1','224.0.0.1','::1','::ffff:8.8.8.8','fc00::1','fe80::1','2001:db8::1','2002:7f00:1::']) assert.equal(publicAddress(ip),false,ip);
  assert.equal(publicAddress('8.8.8.8'),true);
  assert.equal(publicAddress('2606:4700:4700::1111'),true);
  const dns = async()=>[{address:'8.8.8.8',family:4}];
  for (const url of ['file:///etc/passwd','http://127.1','https://2130706433','https://user:pass@example.com','https://example.com:444','https://[::1]']) await assert.rejects(resolvePublicUrl(url,dns));
  await assert.rejects(resolvePublicUrl('https://example.com',async()=>[{address:'8.8.8.8',family:4},{address:'127.0.0.1',family:4}]));
  const target = await resolvePublicUrl('https://example.com/path',dns);
  assert.equal(target.address.address,'8.8.8.8');
  assert.equal(htmlToText('<script>bad()</script><style>x</style><p>Hello &amp; <b>world</b></p>'),'Hello & world');
});
