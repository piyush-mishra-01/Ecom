if (user == 'AnonymousUser') {
    var instance = new Razorpay({
        key_id: 'rzp_test_lD1RsgbizQ5lpQ',
        key_secret: 'jDdLiF2QTGmI4A8asOAbDz2K'
    })
    var options = {
        amount: total,
        currency: "INR",
    };
    instance.orders.create(options, function (err, order) {
        console.log(order);
    });
}
