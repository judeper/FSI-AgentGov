"""Reviewed code-held recovery anchors for regulatory monitor state."""

FINRA_RECOVERY_DUPLICATE_ANCHOR_SCHEMA_VERSION = 1
FINRA_RECOVERY_DUPLICATE_ANCHOR_VERSION = "recovery-2026-08-09-v2"
FINRA_RECOVERY_DUPLICATE_ANCHOR_SOURCE = "regulatory-finra"
FINRA_RECOVERY_DUPLICATE_ANCHOR_SCOPE = (
    "duplicate-nodes-observed-in-reviewed-recovery-2026-08-09"
)
FINRA_RECOVERY_DUPLICATE_ANCHOR_DETAIL_IDENTITY_BINDING_DIGEST = (
    "sha256:4942b9dd838d4e893a1c07ecb140b70de96db7d57f5842e066e95a39195f1c89"
)
FINRA_RECOVERY_DUPLICATE_ANCHOR_RECORD_FIELDS = (
    "canonical_url",
    "canonical_node_identity",
    "authoritative_publication_date",
    "raw_authoritative_proof_hash",
    "substantive_detail_hash",
)
FINRA_RECOVERY_DUPLICATE_ANCHOR_RECORD_COUNT = 55
FINRA_RECOVERY_DUPLICATE_ANCHOR_RECORDS = (
    ('https://www.finra.org/rules-guidance/notices/08-24', 'https://www.finra.org/node/7352', '2008-05-14', 'sha256:73e838a644a4898bb682fde5b18921026f59281947355eacb670c3c30934d8f8', 'sha256:f0e489251561314d374ba95d18543d39375f256ba8404ec3eee6f68f6d0e90a0'),
    ('https://www.finra.org/rules-guidance/notices/08-26', 'https://www.finra.org/node/7354', '2008-05-14', 'sha256:16fe245b9d81af59112b5ae9644424efef78e7cc92fdc0669f31e4eefb832c7c', 'sha256:7dd78711970f1a461620ba51b751aeabb75901cec92a8f3041c92320ff989b22'),
    ('https://www.finra.org/rules-guidance/notices/08-55', 'https://www.finra.org/node/7393', '2008-10-14', 'sha256:7ab6175391b009f5fa46eb7237d39983fc5e1b938d0a677bf1c47e3ed8b8db39', 'sha256:5347668d5a00b71d7a1f0428d6744d4b008055a32a559f3ece3232865867a99a'),
    ('https://www.finra.org/rules-guidance/notices/08-57', 'https://www.finra.org/node/7395', '2008-10-16', 'sha256:de89335bf22b36b90e8b225b22f546fbd43bc40717e69a5c426a075a70d620d4', 'sha256:7b0d5915898d333a7c78e5ab32dee80c1721ef6b79b9d95aca77af57119208ed'),
    ('https://www.finra.org/rules-guidance/notices/08-68', 'https://www.finra.org/node/7412', '2008-11-18', 'sha256:a8faf5108ac7ed3f9d97439f71bdae8cfed613ac756708140cd36c517a2e7a12', 'sha256:af84f3b3183e9701d802635433187b39bd5d3c82b8c78a9df41bb76ddb4039dc'),
    ('https://www.finra.org/rules-guidance/notices/08-69', 'https://www.finra.org/node/7414', '2008-11-26', 'sha256:a65ddf4ccdfccd4757f0cee551c64c9b0bd460518e3cc4fb584e4d4828ef8772', 'sha256:ab40eacec09871fe953a3506f0c6ea0331483fb1ef4dd6f208daf3380355530d'),
    ('https://www.finra.org/rules-guidance/notices/08-71', 'https://www.finra.org/node/7416', '2008-11-28', 'sha256:a4b039aecec68ee7af3ff64ddc88b948bad3ea9864ceb0847939df1ccb3dcb43', 'sha256:a0af60f7111e2ce126f5f89890cf73a3ba51dc4f2cc4c726fe2c13c6a9f0d9d9'),
    ('https://www.finra.org/rules-guidance/notices/08-78', 'https://www.finra.org/node/7425', '2008-12-15', 'sha256:caa7879adb7ddcf1be6424c6ea37760b1697afa5d1030a559d92fe47783c2603', 'sha256:2e0371c0000779fbbc4cbf3163c9ebc1ffafc1b1c13bed26f7e8fda27db72ba4'),
    ('https://www.finra.org/rules-guidance/notices/08-80', 'https://www.finra.org/node/7427', '2008-12-16', 'sha256:4cae3270f79fb252824d6096dbc21793efdaa66768d170f90bb827b0a62281de', 'sha256:515b73e604e4cd7937adaf38862e3e0372d82bca9cbce7719c225da018c68a18'),
    ('https://www.finra.org/rules-guidance/notices/08-83', 'https://www.finra.org/node/7431', '2008-12-24', 'sha256:5400fb8c1595e751c65fe077109dc9548dbac9d731b79b89379151276397766d', 'sha256:7146c8601b973036cf2fd57c944f37d7e3c35a094f9c8511c1f51c29408b9af6'),
    ('https://www.finra.org/rules-guidance/notices/09-02', 'https://www.finra.org/node/7434', '2009-01-06', 'sha256:1419cc53242a0b0e20062e86ca09704bfd7c793d5d12aa44cdb94556faa96d7d', 'sha256:dab889bf6e2d0db3ec20e302d9c6c0f1a9fe3fc58168fbf89b410debc3c6566f'),
    ('https://www.finra.org/rules-guidance/notices/09-11', 'https://www.finra.org/node/7445', '2009-02-17', 'sha256:cae40abfcb0fadee76f16b4355472444a54f1e80328ae3d80ef5efb3b3d2552f', 'sha256:4d9b34fb243a2f7f0f644643c0fc8eade1e91dda80cd768f0197480a9feeedaa'),
    ('https://www.finra.org/rules-guidance/notices/09-15', 'https://www.finra.org/node/7451', '2009-03-12', 'sha256:011ccf35c3ee1ad62ac19e490034f14a38d8141e88154d833201a693a5ab3703', 'sha256:549b88ff96ccedb813ccee82dc9d6621613f0d67803754a5703279343a1bbf73'),
    ('https://www.finra.org/rules-guidance/notices/09-20', 'https://www.finra.org/node/7459', '2009-04-15', 'sha256:27b43b47d6ee4ae8e8d48f56e87e23482f251e140b86b897ea622e5f70e404bc', 'sha256:c129ccff50266f1d41a4d3aefed1e7a87df660afa50bbd00a2c87768ed5d925e'),
    ('https://www.finra.org/rules-guidance/notices/09-22', 'https://www.finra.org/node/7461', '2009-04-21', 'sha256:0221c1275baef719c6a96a00aa7faf6e512235cc9c6c069f34a91bd78a4aa7bf', 'sha256:24f9abc0148d78bede8545fbc16bba56a0c68939e8040eba5454acf0189d1fd6'),
    ('https://www.finra.org/rules-guidance/notices/09-25', 'https://www.finra.org/node/7466', '2009-05-15', 'sha256:60d505024d4fce9b92876ea2b93f85b5115a6972f8ab804e63d6b0cf3a5b2b31', 'sha256:21293c558f9ba14652a72d843994b241e33f6c4cc33329ba28aec4180e8d4b06'),
    ('https://www.finra.org/rules-guidance/notices/09-29', 'https://www.finra.org/node/7471', '2009-06-01', 'sha256:c8e53b76e9feed129e2deabb46bf088438b7c6b949c076b0dbd78c467061acb8', 'sha256:67aad28a05ba367f1c28a0650d2f4c598d8e38c07ccd1cc41eb9d5fe91bc31bb'),
    ('https://www.finra.org/rules-guidance/notices/09-33', 'https://www.finra.org/node/7475', '2009-06-15', 'sha256:28ce2310206812e08fe9c2c4e5a43f9bb3398d51694eb0fe2533a61e904edf47', 'sha256:1cc24b2506481439d3dce397414f05d7df0b5f174d9a3be68c3fd1c6775a8bd3'),
    ('https://www.finra.org/rules-guidance/notices/09-40', 'https://www.finra.org/node/7484', '2009-07-27', 'sha256:d0d30c9b2733a7d127cfc0c808bb1ddd5e1d898e39f710d1a85144bcffcd54c6', 'sha256:14917f3814eeac521ee1c7aaf11235fe1e60a3298158ad386b3f4afbb8705a9b'),
    ('https://www.finra.org/rules-guidance/notices/09-45', 'https://www.finra.org/node/7489', '2009-08-04', 'sha256:5430a568a3375ee511637b49bf34ebacdfde260a33bcbbd7b3d14d20db8a0137', 'sha256:04daf022c3fb935db7319d403c74cbda7947b8b9db119612378819149c5b4e1f'),
    ('https://www.finra.org/rules-guidance/notices/09-50', 'https://www.finra.org/node/7494', '2009-08-17', 'sha256:6e00ddbe8ec0d4e27443a641402402c016fa5e7eb2b24bb657db34b918efc56b', 'sha256:3ef3f1638f36307a98ff7d94071c79ff5f3c4fb4fb34e8f2dd8bb06930965cdf'),
    ('https://www.finra.org/rules-guidance/notices/09-55', 'https://www.finra.org/node/7501', '2009-09-21', 'sha256:cd540ca2e816390ae059c3d59dae9461bd33f7fc7185165045cbdd2b371f57b5', 'sha256:f05b48e3f69cc7a7f09eb70e1363b157ede81efe0a7da3bcfc5b784840cf7343'),
    ('https://www.finra.org/rules-guidance/notices/09-60', 'https://www.finra.org/node/7508', '2009-10-15', 'sha256:542e6381a890f6d93058498df33316425ee100f9ea0d14b10225664061eb9e7f', 'sha256:006cc1df9b3ebbf36a2a7d11b18c0b485134565f7a17b8b48f0f44c5d62cff00'),
    ('https://www.finra.org/rules-guidance/notices/09-63', 'https://www.finra.org/node/7514', '2009-11-12', 'sha256:bae716ac788ef949bf4faa119b6dfe1c70b4dff3d5455003e2eb5ffd9bdae752', 'sha256:676c6d2130a0bd682097ec98e58fd6e92ab2567f126a002b4ff15090d01cbb1d'),
    ('https://www.finra.org/rules-guidance/notices/09-69', 'https://www.finra.org/node/7520', '2009-12-02', 'sha256:6321c49c84f568edb94c79f665608c7e55f79bb667afd9c287ac2b157424c1b5', 'sha256:988610fbda9d04c7b0912e381c237e4c7a062861c0c8fa694b9ac262d04242de'),
    ('https://www.finra.org/rules-guidance/notices/09-72', 'https://www.finra.org/node/7526', '2009-12-15', 'sha256:1a3573fe19106c2bf79b754ca48ae518af40d8b7615373b8150932b10e9a9f8b', 'sha256:309c03ad7f640494c0d6b4691eae35f3de0dab4eb50140e26bb2464831c7b885'),
    ('https://www.finra.org/rules-guidance/notices/10-01', 'https://www.finra.org/node/7532', '2010-01-04', 'sha256:e0e5d0e6f58139296d2cdc53053f4383681002c935588cd00285327cc34ec652', 'sha256:ccb7e7d53e19a1137aea88f8f95da213cf8f31ed367d0f04509a5e5971996081'),
    ('https://www.finra.org/rules-guidance/notices/10-04', 'https://www.finra.org/node/7535', '2010-01-15', 'sha256:d37277c85ef8140417615fa9d5868c0a64e0c005c1adaf67a5ae5ae9cfddeb1c', 'sha256:156c210f0536b8a82bea30d88f9ad8d298f02190f88604f09ead06924fc7df48'),
    ('https://www.finra.org/rules-guidance/notices/10-10', 'https://www.finra.org/node/7543', '2010-02-16', 'sha256:e1c4078363ae27d81f4bbc535866edc7dc4ac87f9cacf03e33d13488c31f5aa7', 'sha256:dcc20b9007b17d2d93ed1a2ec2f184e27edbc17637f36cad7edc7e8d9d400d3c'),
    ('https://www.finra.org/rules-guidance/notices/10-35', 'https://www.finra.org/node/7579', '2010-08-16', 'sha256:44343fc608cd9e324af7558fde47c97c5a18875917da750fb7ee7bea6bb4b66b', 'sha256:b0f4ed5cdaa155a6c3851475b9770a13b13059c8b7fbb4c0feadb707cf623ee0'),
    ('https://www.finra.org/rules-guidance/notices/10-47', 'https://www.finra.org/node/7596', '2010-10-11', 'sha256:b46c10c21779348d1ce280c98e4d77e2cb51dffe2e51cd558122c5836fbed370', 'sha256:48ecdd87090de120e51d1f65bc6d2ac8acf4925f60d6b3de2c2b7db88640ea6f'),
    ('https://www.finra.org/rules-guidance/notices/10-49', 'https://www.finra.org/node/7599', '2010-10-15', 'sha256:0a2154a2b4d5d2252f256972df27f627e45652eca64eff7745b989f539ab30e4', 'sha256:2172edc075ef50bed32621cced5cca75d6f69a5187b17c3278a7447b75ec5b7b'),
    ('https://www.finra.org/rules-guidance/notices/10-53', 'https://www.finra.org/node/7604', '2010-10-26', 'sha256:6c9760579346b0a838e2d9c6e5c08d7ccc530a9cd5a82b629fe2593779d0045a', 'sha256:bd303af367435f097af59886fb4655d9a97d7ab03709ededdf5778b4d031e6da'),
    ('https://www.finra.org/rules-guidance/notices/10-62', 'https://www.finra.org/node/7615', '2010-12-15', 'sha256:1ef6df62f537e909beb20089452f2da5990ad4b81de959656d579f2cc3092ad3', 'sha256:f4b283575db2bee3a4408eae7dc0bd082eecb91b565b492c0d18eabc7a7ce2ed'),
    ('https://www.finra.org/rules-guidance/notices/11-19', 'https://www.finra.org/node/7638', '2011-04-27', 'sha256:e3a8cca70889683f5cb6bed775a096036157d6bcca08ff5c16e0e755c141dd99', 'sha256:1c4da6ec662d8f601c9b6ea6208767683c1d0f37caf68d22af0d8a3488c604cd'),
    ('https://www.finra.org/rules-guidance/notices/11-24', 'https://www.finra.org/node/7645', '2011-05-12', 'sha256:afa210aee6ca314156c5a55c07960c110716af8807e2e514537e6448c3d0a2f3', 'sha256:523059761be92be31709c45ab1a12bcd2ea5eb1e8a86ca57b5e83fea44df47ac'),
    ('https://www.finra.org/rules-guidance/notices/12-04', 'https://www.finra.org/node/7703', '2012-01-18', 'sha256:d17f08745431b06d87904154c1dc8ad01da1d1d92705fe5fddbbf2d7cd58cfb3', 'sha256:7ea87772fcc6afbc52be0af969e737162da197962eec367f80f49657379e958d'),
    ('https://www.finra.org/rules-guidance/notices/12-17', 'https://www.finra.org/node/7721', '2012-04-02', 'sha256:929ad9f38dc20e79a9c427a7fb29641d4b9cedb03aacba06de80a929edeb1b70', 'sha256:a7ce3c80c86946eee4b8a16a197f64a74c4df39529c11fa282a1e31ff601fa8b'),
    ('https://www.finra.org/rules-guidance/notices/12-52', 'https://www.finra.org/node/7773', '2012-12-03', 'sha256:b46d6ce87a27a8b8e99eb4bd9c3eabd6d4c32920de9b51cd31bd655c10f90c05', 'sha256:f0f4ff51aed95169c87611bd2c10d99a9f6f101f5115fb0bd60666bcb9bf52c3'),
    ('https://www.finra.org/rules-guidance/notices/13-07', 'https://www.finra.org/node/7789', '2013-01-31', 'sha256:349fcea2b4bb8f299053f64a78aadd18c17bcd63d65374d9a30f9de5a759f991', 'sha256:f937113963a5d8530a0552e5cf513e49627e948fbf8669288bed87baa912ba26'),
    ('https://www.finra.org/rules-guidance/notices/13-29', 'https://www.finra.org/node/7822', '2013-09-20', 'sha256:34a9c501f09e759b9a46323f88d09562df0aa743ff284d56f9675f557a62e685', 'sha256:149b13f9c9dd0a9282de5b6ca7cd569e2caf99826cc0641cc1b632022a336795'),
    ('https://www.finra.org/rules-guidance/notices/14-07', 'https://www.finra.org/node/7857', '2014-02-14', 'sha256:2bbfd7926e1faf5d1818d7b45150a057216bc1e185e320548507de6b4d03cbe7', 'sha256:9da23d0310adbdd11632794e541b8795f048647e089d04e074293ee477ca8acc'),
    ('https://www.finra.org/rules-guidance/notices/14-26', 'https://www.finra.org/node/7880', '2014-06-27', 'sha256:139b6fb833f11da86740f699c6b4b26411639b6db91620a80b29e44567dbf29c', 'sha256:a9418d23df16816b89d9d94849bb36464916a964a46e804c171c95143286bceb'),
    ('https://www.finra.org/rules-guidance/notices/14-28', 'https://www.finra.org/node/7881', '2014-06-30', 'sha256:a1b37bddcd239c8642fa2e6230e7e784a4885b6053fc7df3d3d5c7a6fdc83c18', 'sha256:37bb2c1e07a7131fbd398cba7e99e50820146790a47d6df555be25694c955066'),
    ('https://www.finra.org/rules-guidance/notices/14-35', 'https://www.finra.org/node/9600', '2014-09-16', 'sha256:ba5c7d6ded878df4bcfb4bec99a7fef3f67da78c5d68647218849d24142ee07a', 'sha256:8d3eec4ccbc682a7ced5cd1dd442f06bd36fc822abd9abe313cb48eb6850c378'),
    ('https://www.finra.org/rules-guidance/notices/15-07', 'https://www.finra.org/node/10768', '2015-03-20', 'sha256:c42adadc755cdcfcf132770a624fdcfd396910ff3a528a1c706abd17e5e6de0a', 'sha256:f4aff20e7877fe6c11a0a4c2aa61bcc21f49e169157be768346570bce403df07'),
    ('https://www.finra.org/rules-guidance/notices/16-22', 'https://www.finra.org/node/65636', '2016-06-30', 'sha256:0f6bbbd80ca33056c87a78d04ae1d79bb38355672425825ab252379f8ea79ca2', 'sha256:8d8b4e44b01c5223c3fbdf0153e96e4a35ba23ad8b443ab75af0b6ea19f8f1da'),
    ('https://www.finra.org/rules-guidance/notices/FYI-03-2003', 'https://www.finra.org/node/126151', '2003-03-07', 'sha256:0be9266d47dbd6a70ac65524e5be815cc2ac31d58bfd07db3775ab6709d9012b', 'sha256:b6e3552b1476c9d3d8cc2c545a494f986eed8ea154586bb6f8c811451ccfd9ba'),
    ('https://www.finra.org/rules-guidance/notices/FYI-10-2002', 'https://www.finra.org/node/126166', '2002-10-18', 'sha256:809691fbdf391a2dfa719cb06a1d4de6defc43865a8a7a5f3b8ae60eaa80d495', 'sha256:734fc3d57a37d714d77718660e9d8b6806f67ca6e91d6ca3cc1d8005032d140a'),
    ('https://www.finra.org/rules-guidance/notices/FYI-12-2000', 'https://www.finra.org/node/126241', '2000-12-11', 'sha256:665b8cdf6f62f42afd6969b320a67f0e192675e21f1bb2b744bfab9d1f49a127', 'sha256:0c07a64a6ebcd28bbb12d5b7b6cbc01015d4de99e490594144f77c7a19cffcba'),
    ('https://www.finra.org/rules-guidance/notices/election-notice-090716', 'https://www.finra.org/node/65983', '2016-09-07', 'sha256:863e13a385a1b519b773dc1bbe8ecd3282504e7fa01439f9ac62e2e49be769a3', 'sha256:e4be2952cfe92a158c025c7959a93fd186863aecd5a5384760cd988170f650b1'),
    ('https://www.finra.org/rules-guidance/notices/election-notice-101613', 'https://www.finra.org/node/7828', '2013-10-16', 'sha256:eadb40feddafeeaf461698a2d79f5c1de06ce382eacb324b78f35c9e67d5f7c5', 'sha256:1fe91b800fa22330e4b3c2da0dae85026346dd3760e29efa08dd5b293a01551a'),
    ('https://www.finra.org/rules-guidance/notices/special-notice%E2%80%9303212017', 'https://www.finra.org/node/66987', '2017-03-21', 'sha256:0d8b7c9c030eab5648dccfd69c10b8ad5bb6dea66a2c55af99cb61055b3ab699', 'sha256:1655160dd6f1564bd4c6c856acee590883c31fa716615e007c78f86fec0098f4'),
    ('https://www.finra.org/rules-guidance/notices/special-notice-07302018', 'https://www.finra.org/node/85960', '2018-07-30', 'sha256:008ced5c8680f0ad920f8b2ccbea30ff5edec71a55786223ed04f57488e83679', 'sha256:ad75b164e12ca466a50c4a551c6bc8b2b707b751106facbaaaa5f7a3202c41f2'),
    ('https://www.finra.org/rules-guidance/notices/y2000-03-1999', 'https://www.finra.org/node/126371', '1999-03-04', 'sha256:2834429379fe0f192af231dfe0633bc62e4700bb477f8037b070e9a80fd85f65', 'sha256:328a710bf532d02035488528362a813847ae1761b543d354c3ff54da7ddc2119'),
)
FINRA_RECOVERY_DUPLICATE_ANCHOR_DIGEST = (
    "sha256:48895b9585b3bc79232e8db4ff39a7a9a56e4a22145511317c8a6f14d6ab1e4b"
)
